use std::path::{Path, PathBuf};
use std::collections::HashMap;
use anyhow::{Result, anyhow};

/// MVP：本机路径。预留枚举供未来多节点扩展。
pub enum Location {
    Local(PathBuf),
}

pub struct Workspace {
    mounts: HashMap<String, Location>,
}

impl Workspace {
    pub fn new() -> Self {
        Workspace { mounts: HashMap::new() }
    }

    /// 挂载一个项目路径。
    pub fn mount(&mut self, name: &str, path: PathBuf) {
        self.mounts.insert(name.to_string(), Location::Local(path));
    }

    /// 获取所有挂载点名称。
    pub fn mount_names(&self) -> Vec<String> {
        self.mounts.keys().cloned().collect()
    }

    /// 获取第一个挂载点的 base 路径（用于兼容旧代码）。
    pub fn first_mount_path(&self) -> Result<PathBuf> {
        let (_, loc) = self.mounts.iter().next()
            .ok_or_else(|| anyhow!("no mounts in workspace"))?;
        match loc {
            Location::Local(p) => Ok(p.clone()),
        }
    }

    /// 解析工作区相对路径，指定 mount name。
    /// "website/README.md" → "/abs/path/to/project/website/README.md"
    /// 支持相对路径（挂载点下的文件）和绝对路径（会检查是否在挂载范围内）。
    pub fn resolve(&self, mount_name: &str, relative: &str) -> Result<PathBuf> {
        let loc = self.mounts.get(mount_name)
            .ok_or_else(|| anyhow!("mount '{}' not found. available: {:?}", mount_name, self.mount_names()))?;

        let base = match loc {
            Location::Local(p) => p.clone(),
        };

        // 如果已经是绝对路径，检查是否在 base 目录下
        if Path::new(relative).is_absolute() {
            let abs = PathBuf::from(relative);
            // 检查是否在 base 内
            if abs.starts_with(&base) {
                return Ok(abs);
            }
            return Err(anyhow!("path '{}' is outside workspace mount '{}' (base: {})", relative, mount_name, base.display()));
        }

        // 相对路径：拼接
        let joined = base.join(relative);

        // 安全检查：canonicalize 后确认仍在 base 下
        // 如果路径不存在，先尝试解析父目录
        if joined.exists() {
            let canonical = std::fs::canonicalize(&joined)
                .map_err(|e| anyhow!("failed to resolve path '{}': {}", relative, e))?;
            let base_canonical = std::fs::canonicalize(&base)
                .unwrap_or(base.clone());

            if canonical.starts_with(&base_canonical) {
                Ok(canonical)
            } else {
                Err(anyhow!("path traversal detected: '{}' escapes workspace mount '{}'", relative, mount_name))
            }
        } else {
            // 路径不存在就信任拼接结果（父目录检查）
            if let Some(parent) = joined.parent() {
                if parent.exists() {
                    let parent_canonical = std::fs::canonicalize(parent)
                        .map_err(|_| anyhow!("failed to resolve parent of '{}'", relative))?;
                    let base_canonical = std::fs::canonicalize(&base)
                        .unwrap_or(base.clone());
                    if !parent_canonical.starts_with(&base_canonical) {
                        return Err(anyhow!("path traversal detected: '{}' escapes workspace mount '{}'", relative, mount_name));
                    }
                }
            }
            Ok(joined)
        }
    }

    /// 生成目录树字符串，用于注入 LLM prompt。
    /// max_depth: 最大深度，0 表示不限。
    pub fn tree(&self, max_depth: usize) -> String {
        fn walk(dir: &Path, prefix: &str, depth: usize, max_depth: usize) -> String {
            if max_depth > 0 && depth >= max_depth {
                return format!("{}└── ...\n", prefix);
            }

            let mut result = String::new();
            if let Ok(entries) = std::fs::read_dir(dir) {
                // 收集所有条目并排序
                let mut items: Vec<_> = entries.filter_map(|e| e.ok()).collect();
                items.sort_by_key(|e| e.file_name());

                for (i, entry) in items.iter().enumerate() {
                    let name = entry.file_name();
                    let name_str = name.to_string_lossy().to_string();

                    // 跳过忽略目录
                    if matches!(name_str.as_str(), ".git" | "node_modules" | "target" | ".venv") {
                        continue;
                    }

                    let is_last = i == items.len() - 1;
                    let connector = if is_last { "└── " } else { "├── " };
                    result.push_str(&format!("{}{}{}\n", prefix, connector, name_str));

                    if entry.file_type().map(|t| t.is_dir()).unwrap_or(false) {
                        let child_prefix = if is_last { "    " } else { "│   " };
                        result.push_str(&walk(&entry.path(), &format!("{}{}", prefix, child_prefix), depth + 1, max_depth));
                    }
                }
            }
            result
        }

        let mut out = String::new();
        for (name, loc) in &self.mounts {
            match loc {
                Location::Local(path) => {
                    out.push_str(&format!("{}:\n", name));
                    out.push_str(&walk(path, "", 0, max_depth));
                }
            }
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    fn setup_test_dir() -> PathBuf {
        let dir = std::env::temp_dir().join("neuralswarm-test-ws");
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(dir.join("src")).unwrap();
        fs::write(dir.join("Cargo.toml"), "").unwrap();
        fs::write(dir.join("src/main.rs"), "").unwrap();
        dir
    }

    #[test]
    fn test_resolve_relative_path() {
        let mut ws = Workspace::new();
        ws.mount("project", PathBuf::from("/home/user/proj"));
        let resolved = ws.resolve("project", "src/main.rs").unwrap();
        assert_eq!(resolved, PathBuf::from("/home/user/proj/src/main.rs"));
    }

    #[test]
    fn test_resolve_absolute_path_inside_mount() {
        let dir = setup_test_dir();
        let mut ws = Workspace::new();
        ws.mount("project", dir.clone());
        // Test with an absolute path inside the mount
        let inside = dir.join("src/main.rs");
        let resolved = ws.resolve("project", inside.to_str().unwrap()).unwrap();
        assert!(resolved.exists());

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn test_resolve_absolute_path_outside_mount() {
        let dir = setup_test_dir();
        let mut ws = Workspace::new();
        ws.mount("project", dir.clone());
        // Create a file outside the mount dir and try to resolve it by absolute path
        let outside = dir.parent().unwrap().join("outsider.txt");
        fs::write(&outside, "").unwrap();
        let result = ws.resolve("project", outside.to_str().unwrap());
        assert!(result.is_err());
        let err = result.unwrap_err().to_string();
        assert!(err.contains("outside workspace"), "expected 'outside workspace', got: {}", err);

        let _ = fs::remove_dir_all(&dir);
        let _ = fs::remove_file(&outside);
    }

    #[test]
    fn test_path_traversal_rejected() {
        let dir = setup_test_dir();
        let mut ws = Workspace::new();
        ws.mount("project", dir.clone());

        // Create a file outside the mount dir to test traversal detection
        let outside_file = dir.parent().unwrap().join("outside_leak.txt");
        fs::write(&outside_file, "leak").unwrap();

        // Use relative traversal "../outside_leak.txt" to reach it
        let result = ws.resolve("project", "../outside_leak.txt");
        assert!(result.is_err());
        if let Err(e) = result {
            let msg = e.to_string();
            assert!(msg.contains("traversal"), "expected 'traversal' in error, got: {}", msg);
        }

        let _ = fs::remove_dir_all(&dir);
        let _ = fs::remove_file(&outside_file);
    }

    #[test]
    fn test_unknown_mount_rejected() {
        let ws = Workspace::new();
        let result = ws.resolve("nonexistent", "file.txt");
        assert!(result.is_err());
    }

    #[test]
    fn test_empty_workspace_fails_resolve() {
        let ws = Workspace::new();
        let result = ws.resolve("project", "src/main.rs");
        assert!(result.is_err());
    }

    #[test]
    fn test_tree_generation() {
        let dir = setup_test_dir();
        let mut ws = Workspace::new();
        ws.mount("test", dir.clone());
        let tree = ws.tree(0);
        assert!(tree.contains("Cargo.toml"));
        assert!(tree.contains("src"));

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn test_tree_with_max_depth() {
        let dir = setup_test_dir();
        let mut ws = Workspace::new();
        ws.mount("test", dir.clone());
        let tree = ws.tree(1);
        assert!(tree.contains("src"));
        // 深度 1 时 src 下的内容应该是 ...
        assert!(tree.contains("..."));

        let _ = fs::remove_dir_all(&dir);
    }
}
