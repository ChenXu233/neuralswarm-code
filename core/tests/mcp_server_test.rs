use neuralswarm_client_core::mcp::tools::get_all_tools;

#[test]
fn test_get_all_tools() {
    let tools = get_all_tools();
    assert_eq!(tools.len(), 5);

    let names: Vec<&str> = tools.iter().map(|t| t.name.as_str()).collect();
    assert!(names.contains(&"file_read"));
    assert!(names.contains(&"file_write"));
    assert!(names.contains(&"shell_execute"));
    assert!(names.contains(&"git_log"));
    assert!(names.contains(&"git_diff"));
}

#[test]
fn test_tool_definitions_have_required_fields() {
    let tools = get_all_tools();
    for tool in &tools {
        assert!(!tool.name.is_empty());
        assert!(!tool.description.is_empty());
        assert!(tool.input_schema.is_object());
    }
}
