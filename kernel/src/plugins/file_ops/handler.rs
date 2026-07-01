use async_trait::async_trait;
use crate::kernel::handler::Handler;
use crate::kernel::context::{Context, ToolResult};
use std::path::PathBuf;

pub struct FileReadHandler;

#[async_trait]
impl Handler for FileReadHandler {
    async fn invoke(&self, mut ctx: Context) -> anyhow::Result<Context> {
        if let Some(call) = ctx.tool_calls.first() {
            let path = call.arguments.get("path")
                .and_then(|v| v.as_str())
                .unwrap_or("");
            match tokio::fs::read_to_string(&path).await {
                Ok(content) => {
                    ctx.tool_results.push(ToolResult {
                        call_id: call.id.clone(),
                        output: content,
                        error: None,
                    });
                }
                Err(e) => {
                    ctx.tool_results.push(ToolResult {
                        call_id: call.id.clone(),
                        output: String::new(),
                        error: Some(format!("read error: {}", e)),
                    });
                }
            }
        }
        Ok(ctx)
    }
}

pub struct FileWriteHandler;

#[async_trait]
impl Handler for FileWriteHandler {
    async fn invoke(&self, mut ctx: Context) -> anyhow::Result<Context> {
        if let Some(call) = ctx.tool_calls.first() {
            let path = call.arguments.get("path")
                .and_then(|v| v.as_str())
                .unwrap_or("");
            let content = call.arguments.get("content")
                .and_then(|v| v.as_str())
                .unwrap_or("");

            if let Some(parent) = PathBuf::from(&path).parent() {
                let _ = tokio::fs::create_dir_all(parent).await;
            }

            match tokio::fs::write(&path, content).await {
                Ok(()) => {
                    ctx.tool_results.push(ToolResult {
                        call_id: call.id.clone(),
                        output: format!("written to {}", path),
                        error: None,
                    });
                }
                Err(e) => {
                    ctx.tool_results.push(ToolResult {
                        call_id: call.id.clone(),
                        output: String::new(),
                        error: Some(format!("write error: {}", e)),
                    });
                }
            }
        }
        Ok(ctx)
    }
}
