pub mod handler;

use std::sync::Arc;
use crate::kernel::registry::{Registry, HandlerRegistration};
use crate::kernel::pipeline::Pipeline;

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
