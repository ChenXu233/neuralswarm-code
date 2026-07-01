pub mod handler;

use crate::kernel::registry::{Registry, HandlerRegistration};
use std::sync::Arc;

pub fn register(registry: &mut Registry) {
    registry.register("tool:file_read", HandlerRegistration {
        id: "file_read".into(),
        handler: Arc::new(handler::FileReadHandler),
        before: vec![],
        after: vec![],
    }).expect("register tool:file_read");

    registry.register("tool:file_write", HandlerRegistration {
        id: "file_write".into(),
        handler: Arc::new(handler::FileWriteHandler),
        before: vec![],
        after: vec![],
    }).expect("register tool:file_write");
}
