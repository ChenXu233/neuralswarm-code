use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolDefinition {
    pub name: String,
    pub description: String,
    pub input_schema: Value,
}

pub fn get_all_tools() -> Vec<ToolDefinition> {
    vec![
        ToolDefinition {
            name: "file_read".to_string(),
            description: "读取文件内容".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"}
                },
                "required": ["path"]
            }),
        },
        ToolDefinition {
            name: "file_write".to_string(),
            description: "写入文件".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "文件内容"}
                },
                "required": ["path", "content"]
            }),
        },
        ToolDefinition {
            name: "shell_execute".to_string(),
            description: "执行 Shell 命令".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell 命令"},
                    "cwd": {"type": "string", "description": "工作目录"}
                },
                "required": ["command"]
            }),
        },
        ToolDefinition {
            name: "git_log".to_string(),
            description: "查看 Git 提交日志".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "仓库路径"},
                    "count": {"type": "integer", "description": "显示数量"}
                },
                "required": ["repo_path"]
            }),
        },
        ToolDefinition {
            name: "git_diff".to_string(),
            description: "查看 Git 差异".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "仓库路径"},
                    "commit_a": {"type": "string", "description": "起始提交"},
                    "commit_b": {"type": "string", "description": "结束提交"}
                },
                "required": ["repo_path"]
            }),
        },
    ]
}
