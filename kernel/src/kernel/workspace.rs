use std::path::{Path, PathBuf};
use std::collections::HashMap;
use anyhow::{Result, anyhow};

/// MVP：本机路径。
/// 预留枚举供未来多节点扩展。
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

    /// 解析工作区相对路径。
    /// "website/README.md" → "/abs/path/to/project/website/README.md"
    pub fn resolve(&self, relative: &str) -> Result<PathBuf> {
        let (_, loc) = self.mounts.iter().next()
            .ok_or_else(|| anyhow!("no mounts in workspace"))?;

        match loc {
            Location::Local(base) => Ok(base.join(relative)),
        }
    }

    /// 生成目录树字符串，用于注入 LLM prompt。
    pub fn tree(&self) -> String {
        fn walk(dir: &Path, prefix: &str) -> String {
            let mut result = String::new();
            if let Ok(entries) = std::fs::read_dir(dir) {
                let mut items: Vec<_> = entries.filter_map(|e| e.ok()).collect();
                items.sort_by_key(|e| e.file_name());

                for (i, entry) in items.iter().enumerate() {
                    let name = entry.file_name();
                    let name_str = name.to_string_lossy().to_string();

                    if matches!(name_str.as_str(), ".git" | "node_modules" | "target" | ".venv") {
                        continue;
                    }

                    let is_last = i == items.len() - 1;
                    let connector = if is_last { "└── " } else { "├── " };
                    result.push_str(&format!("{}{}{}\n", prefix, connector, name_str));

                    if entry.file_type().map(|t| t.is_dir()).unwrap_or(false) {
                        let child_prefix = if is_last { "    " } else { "│   " };
                        result.push_str(&walk(&entry.path(), &format!("{}{}", prefix, child_prefix)));
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
                    out.push_str(&walk(path, ""));
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

    #[test]
    fn test_resolve_relative_path() {
        let mut ws = Workspace::new();
        ws.mount("project", PathBuf::from("/home/user/proj"));
        let resolved = ws.resolve("src/main.rs").unwrap();
        assert_eq!(resolved, PathBuf::from("/home/user/proj/src/main.rs"));
    }

    #[test]
    fn test_empty_workspace_fails_resolve() {
        let ws = Workspace::new();
        let result = ws.resolve("src/main.rs");
        assert!(result.is_err());
    }

    #[test]
    fn test_tree_generation() {
        let dir = std::env::temp_dir().join("neuralswarm-test-ws");
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(dir.join("src")).unwrap();
        fs::write(dir.join("Cargo.toml"), "").unwrap();
        fs::write(dir.join("src/main.rs"), "").unwrap();

        let mut ws = Workspace::new();
        ws.mount("test", dir.clone());
        let tree = ws.tree();
        assert!(tree.contains("Cargo.toml"));
        assert!(tree.contains("src"));

        let _ = fs::remove_dir_all(&dir);
    }
}
