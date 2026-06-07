use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct ServerConfig {
    pub url: String,
    pub token: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ClientConfig {
    #[allow(dead_code)]
    pub name: String,
    pub auto_reconnect: bool,
    #[allow(dead_code)]
    pub heartbeat_interval: u64,
}

#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub server: ServerConfig,
    pub client: ClientConfig,
}

impl Config {
    pub fn from_args(server: String, token: String, name: Option<String>) -> Self {
        Config {
            server: ServerConfig {
                url: server,
                token,
            },
            client: ClientConfig {
                name: name.unwrap_or_else(|| "default-client".to_string()),
                auto_reconnect: true,
                heartbeat_interval: 30,
            },
        }
    }
}
