use std::path::PathBuf;
use std::sync::OnceLock;
use serde::Deserialize;

static CONFIG: OnceLock<Config> = OnceLock::new();

/// 全局配置。初始化后任何地方可通过 `config::get()` 读取。
#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub node: Option<NodeConfig>,
    pub workspace: Option<WorkspaceConfig>,
    pub llm: Option<LlmConfig>,
    pub tools: Option<ToolsConfig>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct NodeConfig {
    pub name: Option<String>,
    pub port: Option<u16>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct WorkspaceConfig {
    pub mounts: Option<Vec<MountConfig>>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct MountConfig {
    pub name: String,
    pub path: PathBuf,
}

#[derive(Debug, Deserialize, Clone)]
pub struct LlmConfig {
    pub api_base: Option<String>,
    pub api_key: Option<String>,
    pub model: Option<String>,
    pub max_iterations: Option<u32>,
    pub system_prompt: Option<String>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ToolsConfig {
    pub shell: Option<ShellConfig>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ShellConfig {
    pub enabled: Option<bool>,
}

impl Config {
    /// 默认配置（所有字段为 None，调用方自行兜底）
    pub fn default() -> Self {
        Config {
            node: None,
            workspace: None,
            llm: None,
            tools: None,
        }
    }

    /// 从 YAML 文件加载配置。
    /// 文件不存在 → 返回默认配置，不报错。
    /// 文件格式错误 → 返回 Err。
    pub fn from_file(path: &str) -> anyhow::Result<Self> {
        let content = match std::fs::read_to_string(path) {
            Ok(c) => c,
            Err(_) => return Ok(Config::default()),
        };
        let mut config: Config = serde_yaml::from_str(&content)?;
        config.resolve_env_vars();
        Ok(config)
    }

    /// 递归替换所有 String 字段中的 ${ENV_VAR} 模式。
    fn resolve_env_vars(&mut self) {
        fn resolve(s: &mut String) {
            let mut result = s.clone();
            while let Some(start) = result.find("${") {
                if let Some(end) = result[start..].find('}') {
                    let var_name: String = result[start + 2..start + end].chars().collect();
                    let env_val = std::env::var(&var_name).unwrap_or_default();
                    result.replace_range(start..start + end + 1, &env_val);
                } else {
                    break;
                }
            }
            *s = result;
        }

        if let Some(ref mut llm) = self.llm {
            if let Some(ref mut key) = llm.api_key {
                resolve(key);
            }
            if let Some(ref mut base) = llm.api_base {
                resolve(base);
            }
        }
    }

    /// 获取 LLM 配置，返回所有字段都有值的完整配置
    pub fn llm_resolved(&self) -> LlmConfig {
        let llm = self.llm.as_ref().cloned().unwrap_or_default();
        LlmConfig {
            api_base: Some(llm.api_base.unwrap_or_else(|| "https://api.openai.com/v1".into())),
            api_key: llm.api_key,
            model: Some(llm.model.unwrap_or_else(|| "gpt-4o-mini".into())),
            max_iterations: Some(llm.max_iterations.unwrap_or(25)),
            system_prompt: llm.system_prompt,
        }
    }
}

impl Default for LlmConfig {
    fn default() -> Self {
        LlmConfig {
            api_base: None,
            api_key: None,
            model: None,
            max_iterations: None,
            system_prompt: None,
        }
    }
}

/// 初始化全局配置。必须在启动时调用一次。
pub fn init(config: Config) {
    CONFIG.set(config).expect("config already initialized");
}

/// 获取全局配置。必须在 init() 之后调用。
pub fn get() -> &'static Config {
    CONFIG.get().expect("config not initialized")
}
