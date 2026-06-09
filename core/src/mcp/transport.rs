use futures_util::{SinkExt, StreamExt};
use serde_json::Value;
use tokio::net::{TcpListener, TcpStream};
use tokio_tungstenite::{accept_async, tungstenite::Message};

pub struct WebSocketTransport {
    addr: String,
}

impl WebSocketTransport {
    pub fn new(addr: &str) -> Self {
        Self {
            addr: addr.to_string(),
        }
    }

    pub async fn start(&self) -> Result<(), Box<dyn std::error::Error>> {
        let listener = TcpListener::bind(&self.addr).await?;
        println!("MCP Server listening on {}", self.addr);

        while let Ok((stream, _)) = listener.accept().await {
            tokio::spawn(handle_connection(stream));
        }
        Ok(())
    }
}

async fn handle_connection(stream: TcpStream) {
    let ws_stream = accept_async(stream).await.unwrap();
    let (mut write, mut read) = ws_stream.split();

    while let Some(msg) = read.next().await {
        let msg = msg.unwrap();
        if let Message::Text(text) = msg {
            let response = handle_request(&text).await;
            write.send(Message::Text(response)).await.unwrap();
        }
    }
}

async fn handle_request(request: &str) -> String {
    let value: Value = serde_json::from_str(request).unwrap_or_default();
    serde_json::json!({
        "jsonrpc": "2.0",
        "id": value.get("id"),
        "result": {}
    })
    .to_string()
}
