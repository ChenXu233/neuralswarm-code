pub mod handler;

use crate::kernel::registry::{Registry, HandlerRegistration};
use std::sync::Arc;

pub fn register(registry: &mut Registry) {
    registry.register("tool:shell", HandlerRegistration {
        id: "shell".into(),
        handler: Arc::new(handler::ShellHandler),
        before: vec![],
        after: vec![],
    }).expect("register tool:shell");
}
