use axum::{
    Router,
    routing::{get, post},
    extract::{State, Path},
    Json,
};
use std::sync::Arc;
use serde::{Deserialize, Serialize};
use crate::kernel::context::{Context, Message};
use super::AppState;

pub fn routes() -> Router<Arc<AppState>> {
    Router::new()
        .route("/api/health", get(health))
        .route("/api/sessions", post(create_session))
        .route("/api/sessions/{id}/messages", post(send_message))
}

async fn health() -> &'static str {
    "ok"
}

#[derive(Serialize)]
struct SessionResponse {
    session_id: String,
}

async fn create_session(
    State(_state): State<Arc<AppState>>,
) -> Json<SessionResponse> {
    Json(SessionResponse {
        session_id: uuid::Uuid::new_v4().to_string(),
    })
}

#[derive(Deserialize)]
struct SendMessageRequest {
    content: String,
}

#[derive(Serialize)]
struct SendMessageResponse {
    status: String,
}

async fn send_message(
    State(state): State<Arc<AppState>>,
    Path(_session_id): Path<String>,
    Json(req): Json<SendMessageRequest>,
) -> Json<serde_json::Value> {
    let ctx = Context {
        session_id: uuid::Uuid::new_v4().to_string(),
        trace_id: uuid::Uuid::new_v4().to_string(),
        messages: vec![Message {
            role: "user".into(),
            content: req.content,
            tool_calls: None,
            tool_call_id: None,
        }],
        tool_calls: vec![],
        tool_results: vec![],
        terminated: false,
        extras: std::collections::HashMap::new(),
    };

    match state.pipeline.invoke("user-message", ctx).await {
        Ok(_ctx) => Json(serde_json::json!({"status": "ok"})),
        Err(e) => Json(serde_json::json!({"error": e.to_string()})),
    }
}
