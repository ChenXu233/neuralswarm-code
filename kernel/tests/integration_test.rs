/// 集成测试：启动 kernel → 创建 session → 发送消息 → 验证完整流程
///
/// 注意：这些测试需要运行中的 kernel 实例。
/// 通过 `KERNEL_URL` 环境变量指定地址，默认为 http://localhost:8080

use std::env;

const DEFAULT_URL: &str = "http://localhost:8080";

fn base_url() -> String {
    env::var("KERNEL_URL").unwrap_or_else(|_| DEFAULT_URL.to_string())
}

#[tokio::test]
async fn test_health_endpoint() {
    let client = reqwest::Client::new();
    let resp = client
        .get(format!("{}/api/health", base_url()))
        .send()
        .await
        .expect("health endpoint should respond");

    assert!(resp.status().is_success());
    let text = resp.text().await.unwrap();
    assert_eq!(text, "ok");
}

#[tokio::test]
async fn test_create_session() {
    let client = reqwest::Client::new();
    let resp = client
        .post(format!("{}/api/sessions", base_url()))
        .send()
        .await
        .expect("create session should respond");

    assert!(resp.status().is_success());
    let json: serde_json::Value = resp.json().await.unwrap();
    assert!(json.get("session_id").is_some());
    let sid = json["session_id"].as_str().unwrap().to_string();
    assert!(!sid.is_empty(), "session_id should not be empty");
}

#[tokio::test]
async fn test_send_message() {
    let client = reqwest::Client::new();

    // 先创建 session
    let create_resp = client
        .post(format!("{}/api/sessions", base_url()))
        .send()
        .await
        .unwrap();
    let create_json: serde_json::Value = create_resp.json().await.unwrap();
    let session_id = create_json["session_id"].as_str().unwrap().to_string();

    // 发送消息
    let msg_resp = client
        .post(format!("{}/api/sessions/{}/messages", base_url(), session_id))
        .json(&serde_json::json!({"content": "hello"}))
        .send()
        .await
        .unwrap();

    assert!(msg_resp.status().is_success());
    let msg_json: serde_json::Value = msg_resp.json().await.unwrap();
    assert!(msg_json.get("status").is_some());
}
