use std::collections::HashMap;
use std::sync::Mutex;
use tokio::sync::mpsc;
use axum::extract::ws::{Message, WebSocket};
use axum::extract::{State, Path, WebSocketUpgrade};
use axum::response::IntoResponse;
use std::sync::Arc;
use futures_util::{SinkExt, StreamExt};
use crate::server::AppState;

/// 全局 WebSocket 连接管理器。
pub struct WssManager {
    sessions: Mutex<HashMap<String, Vec<mpsc::UnboundedSender<String>>>>,
}

impl WssManager {
    pub fn new() -> Self {
        WssManager {
            sessions: Mutex::new(HashMap::new()),
        }
    }

    pub fn subscribe(&self, session_id: &str, sender: mpsc::UnboundedSender<String>) {
        let mut sessions = self.sessions.lock().unwrap();
        sessions.entry(session_id.to_string()).or_default().push(sender);
    }

    pub fn unsubscribe(&self, session_id: &str, sender_id: usize) {
        let mut sessions = self.sessions.lock().unwrap();
        if let Some(conns) = sessions.get_mut(session_id) {
            conns.retain(|s| s as *const _ as usize != sender_id);
            if conns.is_empty() {
                sessions.remove(session_id);
            }
        }
    }

    pub fn push(&self, session_id: &str, event_json: String) {
        let sessions = self.sessions.lock().unwrap();
        if let Some(conns) = sessions.get(session_id) {
            for sender in conns {
                let _ = sender.send(event_json.clone());
            }
        }
    }

    #[allow(dead_code)]
    pub fn connection_count(&self, session_id: &str) -> usize {
        let sessions = self.sessions.lock().unwrap();
        sessions.get(session_id).map(|c| c.len()).unwrap_or(0)
    }
}

pub fn ws_routes() -> axum::Router<Arc<AppState>> {
    axum::Router::new()
        .route("/ws/sessions/{session_id}", axum::routing::get(ws_handler))
}

async fn ws_handler(
    ws: WebSocketUpgrade,
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
) -> impl IntoResponse {
    ws.on_upgrade(move |socket| handle_socket(socket, session_id, state))
}

async fn handle_socket(socket: WebSocket, session_id: String, state: Arc<AppState>) {
    let (mut sender, mut receiver) = socket.split();
    let (tx, mut rx) = mpsc::unbounded_channel::<String>();

    let sender_id = &tx as *const _ as usize;
    state.wss_manager.subscribe(&session_id, tx.clone());

    // 发送已有消息历史
    if let Ok(msgs) = state.store.get_messages(&session_id) {
        for msg in &msgs {
            let _ = tx.send(serde_json::json!({
                "type": "message",
                "data": { "content": msg.content, "role": msg.role },
                "history": true,
            }).to_string());
        }
    }

    // 将发送任务放在后台，主任务处理接收
    let send_handle = tokio::spawn(async move {
        while let Some(msg) = rx.recv().await {
            if sender.send(Message::Text(msg.into())).await.is_err() {
                break;
            }
        }
    });

    // 主任务：等待客户端断开或收到关闭/心跳帧
    while let Some(Ok(msg)) = receiver.next().await {
        match msg {
            Message::Close(_) | Message::Ping(_) | Message::Pong(_) => break,
            _ => {}
        }
    }

    // 连接断开，终止发送任务
    send_handle.abort();

    state.wss_manager.unsubscribe(&session_id, sender_id);
}