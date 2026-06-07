use neuralswarm_client_core::executor::{self, ExecuteParams};

#[tokio::test]
async fn test_file_read_nonexistent() {
    let params = ExecuteParams {
        path: Some("/nonexistent/file.txt".to_string()),
        content: None,
        command: None,
        timeout: None,
    };
    let result = executor::execute("file_read", &params, "req-001").await;
    assert_eq!(result.status, "error");
    assert_eq!(result.request_id, "req-001");
}

#[tokio::test]
async fn test_unknown_command() {
    let params = ExecuteParams {
        path: None,
        content: None,
        command: None,
        timeout: None,
    };
    let result = executor::execute("unknown_cmd", &params, "req-002").await;
    assert_eq!(result.status, "error");
    assert!(result.data["message"].as_str().unwrap().contains("Unknown command"));
}

#[tokio::test]
async fn test_shell_echo() {
    let params = ExecuteParams {
        path: None,
        content: None,
        command: Some("echo hello".to_string()),
        timeout: Some(5),
    };
    let result = executor::execute("shell", &params, "req-003").await;
    assert_eq!(result.status, "success");
    assert!(result.data["output"].as_str().unwrap().contains("hello"));
}

#[tokio::test]
async fn test_file_write_and_read() {
    use std::fs;
    let test_path = std::env::temp_dir().join("neuralswarm_test_file.txt");
    let test_path_str = test_path.to_string_lossy().to_string();

    // Write
    let write_params = ExecuteParams {
        path: Some(test_path_str.clone()),
        content: Some("test content".to_string()),
        command: None,
        timeout: None,
    };
    let write_result = executor::execute("file_write", &write_params, "req-004").await;
    assert_eq!(write_result.status, "success");

    // Read
    let read_params = ExecuteParams {
        path: Some(test_path_str.clone()),
        content: None,
        command: None,
        timeout: None,
    };
    let read_result = executor::execute("file_read", &read_params, "req-005").await;
    assert_eq!(read_result.status, "success");
    assert_eq!(read_result.data["content"].as_str().unwrap(), "test content");

    // Cleanup
    let _ = fs::remove_file(&test_path);
}
