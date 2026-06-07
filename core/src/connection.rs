use futures_util::{SinkExt, StreamExt};
use serde_json::Value;
use tokio_tungstenite::{connect_async, tungstenite::Message};
use tracing::{info, error};
use anyhow::Result;

use crate::config::Config;
use crate::executor::{self, ExecuteParams};

pub async fn run(config: Config) -> Result<()> {
    let url = format!("{}?token={}", config.server.url, config.server.token);
    info!("Connecting to {}", config.server.url);

    loop {
        match connect_and_run(&url, &config).await {
            Ok(()) => {
                if !config.client.auto_reconnect {
                    break;
                }
                info!("Disconnected, reconnecting in 5s...");
                tokio::time::sleep(std::time::Duration::from_secs(5)).await;
            }
            Err(e) => {
                error!("Connection error: {}", e);
                if !config.client.auto_reconnect {
                    break;
                }
                info!("Reconnecting in 5s...");
                tokio::time::sleep(std::time::Duration::from_secs(5)).await;
            }
        }
    }
    Ok(())
}

async fn connect_and_run(url: &str, _config: &Config) -> Result<()> {
    let (ws_stream, _) = connect_async(url).await?;
    let (mut write, mut read) = ws_stream.split();

    info!("Connected to server");

    while let Some(msg) = read.next().await {
        let msg = msg?;
        match msg {
            Message::Text(text) => {
                let data: Value = serde_json::from_str(&text)?;
                if data["type"] == "execute" {
                    let command = data["command"].as_str().unwrap_or("");
                    let params: ExecuteParams = serde_json::from_value(data["params"].clone())?;
                    let request_id = data["request_id"].as_str().unwrap_or("");

                    info!("Executing: {} (request_id: {})", command, request_id);

                    let result = executor::execute(command, &params, request_id).await;
                    let response = serde_json::to_string(&result)?;
                    write.send(Message::Text(response)).await?;
                }
            }
            Message::Ping(data) => {
                write.send(Message::Pong(data)).await?;
            }
            Message::Close(_) => {
                info!("Server closed connection");
                break;
            }
            _ => {}
        }
    }

    Ok(())
}
