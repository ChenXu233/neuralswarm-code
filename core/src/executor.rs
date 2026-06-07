use serde::{Deserialize, Serialize};
use std::time::Duration;
use tokio::fs;
use anyhow::Result;

#[derive(Debug, Deserialize)]
pub struct ExecuteParams {
    pub path: Option<String>,
    pub content: Option<String>,
    pub command: Option<String>,
    pub timeout: Option<u64>,
}

#[derive(Debug, Serialize)]
pub struct ExecuteResult {
    pub request_id: String,
    pub status: String,
    pub data: serde_json::Value,
}

pub async fn execute(command: &str, params: &ExecuteParams, request_id: &str) -> ExecuteResult {
    let result = match command {
        "file_read" => file_read(params).await,
        "file_write" => file_write(params).await,
        "shell" => shell(params).await,
        _ => Err(anyhow::anyhow!("Unknown command: {}", command)),
    };

    match result {
        Ok(data) => ExecuteResult {
            request_id: request_id.to_string(),
            status: "success".to_string(),
            data,
        },
        Err(e) => ExecuteResult {
            request_id: request_id.to_string(),
            status: "error".to_string(),
            data: serde_json::json!({"message": e.to_string()}),
        },
    }
}

async fn file_read(params: &ExecuteParams) -> Result<serde_json::Value> {
    let path = params.path.as_ref().ok_or_else(|| anyhow::anyhow!("path required"))?;
    let content = fs::read_to_string(path).await?;
    Ok(serde_json::json!({"content": content}))
}

async fn file_write(params: &ExecuteParams) -> Result<serde_json::Value> {
    let path = params.path.as_ref().ok_or_else(|| anyhow::anyhow!("path required"))?;
    let content = params.content.as_ref().ok_or_else(|| anyhow::anyhow!("content required"))?;
    if let Some(parent) = std::path::Path::new(path).parent() {
        fs::create_dir_all(parent).await?;
    }
    fs::write(path, content).await?;
    Ok(serde_json::json!({"message": format!("Written to {}", path)}))
}

async fn shell(params: &ExecuteParams) -> Result<serde_json::Value> {
    let command = params.command.as_ref().ok_or_else(|| anyhow::anyhow!("command required"))?;
    let timeout_secs = params.timeout.unwrap_or(30);

    let output = tokio::time::timeout(
        Duration::from_secs(timeout_secs),
        tokio::process::Command::new("sh")
            .arg("-c")
            .arg(command)
            .output(),
    )
    .await
    .map_err(|_| anyhow::anyhow!("Command timed out"))?
    .map_err(|e| anyhow::anyhow!("Failed to execute: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();
    let result = if stderr.is_empty() { stdout } else { format!("{}\n{}", stdout, stderr) };

    Ok(serde_json::json!({"output": result.trim()}))
}
