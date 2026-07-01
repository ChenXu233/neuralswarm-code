use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use serde_json::Value;

/// 流经管道的唯一数据载体。
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Context {
    pub session_id: String,
    pub workspace_path: String,
    pub trace_id: String,
    pub messages: Vec<Message>,
    pub tool_calls: Vec<ToolCall>,
    pub tool_results: Vec<ToolResult>,
    pub terminated: bool,
    pub extras: HashMap<String, Value>,
}

impl Context {
    pub fn new(session_id: &str, workspace_path: &str) -> Self {
        Context {
            session_id: session_id.to_string(),
            workspace_path: workspace_path.to_string(),
            trace_id: uuid::Uuid::new_v4().to_string(),
            messages: Vec::new(),
            tool_calls: Vec::new(),
            tool_results: Vec::new(),
            terminated: false,
            extras: HashMap::new(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
    pub tool_calls: Option<Vec<ToolCall>>,
    pub tool_call_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCall {
    pub id: String,
    pub name: String,
    pub arguments: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolResult {
    pub call_id: String,
    pub output: String,
    pub error: Option<String>,
}
