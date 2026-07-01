use axum::{
    Router,
    routing::get,
    extract::{State, Path},
    Json,
};
use std::sync::Arc;
use serde::{Deserialize, Serialize};
use crate::kernel::context::{Context, Message};
use crate::storage::session_store::StoredMessage;
use super::AppState;

pub fn routes() -> Router<Arc<AppState>> {
    Router::new()
        .route("/api/health", get(health))
        .route("/api/sessions", get(list_sessions).post(create_session))
        .route("/api/sessions/:id/messages", get(get_session_messages).post(send_message))
}

async fn health() -> &'static str {
    "ok"
}

// ── Sessions ────────────────────────────────────────────────

async fn create_session(
    State(state): State<Arc<AppState>>,
) -> Json<serde_json::Value> {
    let id = uuid::Uuid::new_v4().to_string();
    let ws_path = &state.default_workspace_path;

    match state.store.create_session(&id, ws_path) {
        Ok(()) => Json(serde_json::json!({"session_id": id})),
        Err(e) => Json(serde_json::json!({"error": e.to_string()})),
    }
}

#[derive(Serialize)]
struct SessionListItem {
    id: String,
    workspace_path: String,
    created_at: String,
    updated_at: String,
    message_count: i64,
}

async fn list_sessions(
    State(state): State<Arc<AppState>>,
) -> Json<serde_json::Value> {
    match state.store.list_sessions() {
        Ok(sessions) => {
            let items: Vec<SessionListItem> = sessions.into_iter().map(|s| SessionListItem {
                id: s.id,
                workspace_path: s.workspace_path,
                created_at: s.created_at,
                updated_at: s.updated_at,
                message_count: s.message_count,
            }).collect();
            Json(serde_json::json!({"sessions": items}))
        }
        Err(e) => Json(serde_json::json!({"error": e.to_string()})),
    }
}

// ── Messages ────────────────────────────────────────────────

#[derive(Deserialize)]
struct SendMessageRequest {
    content: String,
}

async fn send_message(
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
    Json(req): Json<SendMessageRequest>,
) -> Json<serde_json::Value> {
    // 1. 验证 session 存在
    let _session = match state.store.get_session(&session_id) {
        Ok(Some(s)) => s,
        Ok(None) => return Json(serde_json::json!({"error": "session not found"})),
        Err(e) => return Json(serde_json::json!({"error": e.to_string()})),
    };

    // 2. 保存用户消息到 DB
    let user_msg = StoredMessage {
        role: "user".into(),
        content: req.content.clone(),
        tool_calls: None,
        tool_call_id: None,
    };
    if let Err(e) = state.store.add_message(&session_id, &user_msg) {
        return Json(serde_json::json!({"error": format!("failed to save message: {}", e)}));
    }

    // 3. 从 DB 加载完整历史
    let history = match state.store.get_messages(&session_id) {
        Ok(h) => h,
        Err(e) => return Json(serde_json::json!({"error": e.to_string()})),
    };

    // 4. 构建 Context（含完整历史）
    let trace_id = uuid::Uuid::new_v4().to_string();
    let mut messages: Vec<Message> = Vec::new();

    // 插入 system message（如果配置了）
    if let Some(llm_cfg) = crate::config::get().llm.as_ref() {
        if let Some(ref sp) = llm_cfg.system_prompt {
            messages.push(Message {
                role: "system".into(),
                content: sp.clone(),
                tool_calls: None,
                tool_call_id: None,
            });
        }
    }

    // 从历史记录转换
    for stored in &history {
        messages.push(Message {
            role: stored.role.clone(),
            content: stored.content.clone(),
            tool_calls: stored.tool_calls.clone(),
            tool_call_id: stored.tool_call_id.clone(),
        });
    }

    let ctx = Context {
        session_id: session_id.clone(),
        workspace_path: _session.workspace_path.clone(),
        trace_id,
        messages,
        tool_calls: vec![],
        tool_results: vec![],
        terminated: false,
        extras: std::collections::HashMap::new(),
    };

    // 5. Pipeline 执行
    let result_ctx = match state.pipeline.invoke("llm-prompt", ctx).await {
        Ok(ctx) => ctx,
        Err(e) => return Json(serde_json::json!({"error": e.to_string()})),
    };

    // 6. 把 pipeline 产生的新消息写回 DB（跳过已有的 history.len() 条）
    let msg_count_before = match crate::config::get().llm.as_ref().and_then(|l| l.system_prompt.as_ref()) {
        Some(_) => history.len() + 1,  // + system prompt
        None => history.len(),
    };

    for msg in &result_ctx.messages[msg_count_before..] {
        if let Err(e) = state.store.add_message(&session_id, &StoredMessage {
            role: msg.role.clone(),
            content: msg.content.clone(),
            tool_calls: msg.tool_calls.clone(),
            tool_call_id: msg.tool_call_id.clone(),
        }) {
            return Json(serde_json::json!({"error": format!("failed to save result: {}", e)}));
        }
    }

    // 7. 提取最后一条 assistant 消息作为响应
    let response = result_ctx.messages.iter().rev()
        .find(|m| m.role == "assistant")
        .map(|m| m.content.clone())
        .unwrap_or_default();

    Json(serde_json::json!({
        "session_id": session_id,
        "response": response,
        "message_count": result_ctx.messages.len(),
    }))
}

/// 获取会话的消息历史
async fn get_session_messages(
    State(state): State<Arc<AppState>>,
    Path(session_id): Path<String>,
) -> Json<serde_json::Value> {
    match state.store.get_messages(&session_id) {
        Ok(msgs) => {
            let items: Vec<serde_json::Value> = msgs.into_iter().map(|m| {
                serde_json::json!({
                    "role": m.role,
                    "content": m.content,
                    "tool_calls": m.tool_calls,
                    "tool_call_id": m.tool_call_id,
                })
            }).collect();
            Json(serde_json::json!({"messages": items}))
        }
        Err(e) => Json(serde_json::json!({"error": e.to_string()})),
    }
}
