pub mod handler;

use std::sync::Arc;
use crate::kernel::registry::{Registry, HandlerRegistration};
use crate::kernel::pipeline::Pipeline;
use crate::server::ws::WssManager;

pub fn register_handler(registry: &mut Registry) {
    registry.register("llm-prompt", HandlerRegistration {
        id: "llm".into(),
        handler: Arc::new(handler::LLMHandler),
        before: vec![],
        after: vec![],
    }).expect("register llm-prompt");
}

pub fn set_pipeline(pipeline: Arc<Pipeline>) {
    handler::set_pipeline(pipeline);
}

pub fn set_wss_manager(manager: Arc<WssManager>) {
    handler::set_wss_manager(manager);
}
