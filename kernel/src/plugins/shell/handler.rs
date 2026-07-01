use async_trait::async_trait;
use crate::kernel::handler::Handler;
use crate::kernel::context::{Context, ToolResult};
use std::time::Duration;

pub struct ShellHandler;

#[async_trait]
impl Handler for ShellHandler {
    async fn invoke(&self, mut ctx: Context) -> anyhow::Result<Context> {
        if let Some(call) = ctx.tool_calls.first() {
            let command = call.arguments.get("command")
                .and_then(|v| v.as_str())
                .unwrap_or("");
            let timeout = call.arguments.get("timeout")
                .and_then(|v| v.as_u64())
                .unwrap_or(30);

            match execute_shell(command, timeout).await {
                Ok(output) => {
                    ctx.tool_results.push(ToolResult {
                        call_id: call.id.clone(),
                        output,
                        error: None,
                    });
                }
                Err(e) => {
                    ctx.tool_results.push(ToolResult {
                        call_id: call.id.clone(),
                        output: String::new(),
                        error: Some(e),
                    });
                }
            }
        }
        Ok(ctx)
    }
}

async fn execute_shell(command: &str, timeout_secs: u64) -> Result<String, String> {
    let output = tokio::time::timeout(
        Duration::from_secs(timeout_secs),
        tokio::process::Command::new("sh")
            .arg("-c")
            .arg(command)
            .output(),
    ).await.map_err(|_| "command timed out".to_string())?
      .map_err(|e| e.to_string())?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    let result = if stderr.is_empty() {
        stdout.to_string()
    } else {
        format!("{}\n{}", stdout, stderr)
    };
    Ok(result.trim().to_string())
}
