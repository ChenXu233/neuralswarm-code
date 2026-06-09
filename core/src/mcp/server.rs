use super::tools::get_all_tools;
use super::transport::WebSocketTransport;

pub struct McpServer {
    transport: WebSocketTransport,
}

impl McpServer {
    pub fn new(addr: &str) -> Self {
        Self {
            transport: WebSocketTransport::new(addr),
        }
    }

    pub async fn start(&self) -> Result<(), Box<dyn std::error::Error>> {
        println!("Starting MCP Server...");
        println!(
            "Available tools: {:?}",
            get_all_tools().iter().map(|t| &t.name).collect::<Vec<_>>()
        );
        self.transport.start().await
    }
}
