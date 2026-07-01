use std::sync::Arc;
use std::sync::OnceLock;
use async_trait::async_trait;
use serde_json::Value;
use crate::kernel::handler::Handler;
use crate::kernel::context::{Context, Message, ToolCall};
use crate::kernel::pipeline::Pipeline;

static PIPELINE: OnceLock<Arc<Pipeline>> = OnceLock::new();

pub fn set_pipeline(pipeline: Arc<Pipeline>) {
    if PIPELINE.set(pipeline).is_err() {
        // Already set — safe to ignore
    }
}

pub fn get_pipeline() -> &'static Arc<Pipeline> {
    PIPELINE.get().expect("pipeline not initialized")
}

pub struct LLMHandler;

#[async_trait]
impl Handler for LLMHandler {
    async fn invoke(&self, mut ctx: Context) -> anyhow::Result<Context> {
        let llm_cfg = crate::config::get().llm_resolved();
        let api_base = llm_cfg.api_base.unwrap_or_else(|| "https://api.openai.com/v1".into());
        let api_key = llm_cfg.api_key.unwrap_or_default();
        let model = llm_cfg.model.unwrap_or_else(|| "gpt-4o-mini".into());
        let max_iterations = llm_cfg.max_iterations.unwrap_or(25);

        let client = reqwest::Client::new();

        // Convert ctx.messages to OpenAI API format
        let mut openai_messages: Vec<Value> = ctx.messages.iter().map(|m| {
            let mut msg = serde_json::json!({
                "role": m.role,
                "content": m.content,
            });
            if let Some(ref tcs) = m.tool_calls {
                msg["tool_calls"] = serde_json::json!(tcs.iter().map(|tc| {
                    serde_json::json!({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": tc.arguments.to_string(),
                        }
                    })
                }).collect::<Vec<_>>());
            }
            if let Some(ref tcid) = m.tool_call_id {
                msg["tool_call_id"] = serde_json::json!(tcid);
            }
            msg
        }).collect();

        // 如果有 system_prompt 配置，插入到消息列表开头
        if let Some(ref sp) = llm_cfg.system_prompt {
            if !openai_messages.iter().any(|m| m["role"] == "system") {
                openai_messages.insert(0, serde_json::json!({
                    "role": "system",
                    "content": sp,
                }));
            }
        }

        // Agent loop — 最多 max_iterations 轮
        for _iteration in 0..max_iterations {
            // Tool schemas for LLM — dynamically fetched from Registry
            let tools = get_pipeline().registry_ref().get_tool_schemas();

            // Build request body
            let body = serde_json::json!({
                "model": model,
                "messages": openai_messages,
                "tools": tools,
                "tool_choice": "auto",
            });

            // HTTP call
            let url = format!("{}/chat/completions", api_base.trim_end_matches('/'));
            let resp = client.post(&url)
                .header("Content-Type", "application/json")
                .header("Authorization", format!("Bearer {}", api_key))
                .json(&body)
                .send()
                .await
                .map_err(|e| anyhow::anyhow!("LLM request failed: {}", e))?;

            if !resp.status().is_success() {
                let status = resp.status();
                let text = resp.text().await.unwrap_or_default();
                return Err(anyhow::anyhow!("LLM API error {}: {}", status, text));
            }

            let data: Value = resp.json().await
                .map_err(|e| anyhow::anyhow!("LLM response parse error: {}", e))?;

            // Extract content and tool calls
            let choice = &data["choices"][0];
            let message = &choice["message"];
            let content = message["content"].as_str().unwrap_or("").to_string();
            let tool_calls = message["tool_calls"].as_array()
                .map(|arr| arr.iter().map(|tc| {
                    // OpenAI API 的 arguments 是 JSON 字符串，需要解析成对象
                    let args_str = tc["function"]["arguments"].as_str().unwrap_or("{}");
                    let args: Value = serde_json::from_str(args_str).unwrap_or(Value::Object(Default::default()));
                    ToolCall {
                        id: tc["id"].as_str().unwrap_or("").to_string(),
                        name: tc["function"]["name"].as_str().unwrap_or("").to_string(),
                        arguments: args,
                    }
                }).collect::<Vec<_>>())
                .unwrap_or_default();

            if tool_calls.is_empty() {
                // LLM text response done
                ctx.messages.push(Message {
                    role: "assistant".into(),
                    content: content.clone(),
                    tool_calls: None,
                    tool_call_id: None,
                });
                return Ok(ctx);
            }

            // Add assistant message with tool calls to ctx
            ctx.messages.push(Message {
                role: "assistant".into(),
                content: content.clone(),
                tool_calls: Some(tool_calls.clone()),
                tool_call_id: None,
            });

            // Add to OpenAI messages for next iteration
            openai_messages.push(serde_json::json!({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls.iter().map(|tc| {
                    serde_json::json!({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": tc.arguments.to_string(),
                        }
                    })
                }).collect::<Vec<_>>()
            }));

            // Execute each tool call through pipeline
            for tc in &tool_calls {
                let tool_point = format!("tool:{}", tc.name);

                let tool_ctx = Context {
                    session_id: ctx.session_id.clone(),
                    workspace_path: ctx.workspace_path.clone(),
                    trace_id: ctx.trace_id.clone(),
                    messages: vec![],
                    tool_calls: vec![tc.clone()],
                    tool_results: vec![],
                    terminated: false,
                    extras: std::collections::HashMap::new(),
                };

                let result = match get_pipeline().invoke(&tool_point, tool_ctx).await {
                    Ok(res_ctx) => {
                        res_ctx.tool_results.first()
                            .map(|r| {
                                if let Some(ref err) = r.error {
                                    format!("Error: {}", err)
                                } else {
                                    r.output.clone()
                                }
                            })
                            .unwrap_or_else(|| format!("Error: unknown tool '{}'", tc.name))
                    }
                    Err(e) => format!("Error: {}", e),
                };

                // Add to ctx.messages
                ctx.messages.push(Message {
                    role: "tool".into(),
                    content: result.clone(),
                    tool_calls: None,
                    tool_call_id: Some(tc.id.clone()),
                });

                // Add to OpenAI messages
                openai_messages.push(serde_json::json!({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }));
            }

            // Loop continues: send updated messages back to LLM
        }

        // 循环耗尽，未得到文本回复
        Err(anyhow::anyhow!("LLM agent loop exceeded max iterations ({})", max_iterations))
    }
}
