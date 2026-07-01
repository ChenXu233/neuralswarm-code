use std::sync::Arc;
use anyhow::Result;
use crate::kernel::context::Context;
use crate::kernel::registry::Registry;

/// 管道引擎。
/// 流经过一个点时，按拓扑序调用该点上的所有 handler。
pub struct Pipeline {
    registry: Arc<Registry>,
}

impl Pipeline {
    pub fn new(registry: Registry) -> Self {
        Pipeline { registry: Arc::new(registry) }
    }

    pub fn registry_ref(&self) -> &Registry {
        &*self.registry
    }

    /// 让流经过指定点。
    pub async fn invoke(&self, point: &str, mut ctx: Context) -> Result<Context> {
        let handlers = self.registry.get_handlers(point)?.to_vec();
        for handler in &handlers {
            if ctx.terminated {
                break;
            }
            ctx = handler.invoke(ctx).await?;
        }
        Ok(ctx)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::kernel::registry::{Registry, HandlerRegistration};
    use crate::kernel::handler::Handler;
    use crate::kernel::context::Context;
    use std::sync::Arc;
    use std::sync::atomic::{AtomicUsize, Ordering};

    struct CounterHandler {
        count: Arc<AtomicUsize>,
    }

    #[async_trait::async_trait]
    impl Handler for CounterHandler {
        async fn invoke(&self, mut ctx: Context) -> Result<Context> {
            self.count.fetch_add(1, Ordering::SeqCst);
            ctx.extras.insert("called".into(), serde_json::json!(self.count.load(Ordering::SeqCst)));
            Ok(ctx)
        }
    }

    #[tokio::test]
    async fn test_pipeline_invokes_handlers_in_order() {
        let mut reg = Registry::new();
        let count = Arc::new(AtomicUsize::new(0));

        reg.register("llm-prompt", HandlerRegistration {
            id: "h1".into(),
            handler: Arc::new(CounterHandler { count: count.clone() }),
            before: vec![],
            after: vec![],
        }).unwrap();

        let pipeline = Pipeline::new(reg);
        let ctx = Context {
            session_id: "test".into(),
            trace_id: "test".into(),
            messages: vec![],
            tool_calls: vec![],
            tool_results: vec![],
            terminated: false,
            extras: std::collections::HashMap::new(),
        };

        let ctx = pipeline.invoke("llm-prompt", ctx).await.unwrap();
        assert_eq!(count.load(Ordering::SeqCst), 1);
    }

    #[tokio::test]
    async fn test_terminated_stops_pipeline() {
        let mut reg = Registry::new();

        reg.register("tool-execute.before", HandlerRegistration {
            id: "blocker".into(),
            handler: Arc::new(BlockerHandler),
            before: vec![],
            after: vec![],
        }).unwrap();
        reg.register("tool-execute.before", HandlerRegistration {
            id: "should-not-run".into(),
            handler: Arc::new(ShouldNotRunHandler),
            before: vec![],
            after: vec![],
        }).unwrap();

        let pipeline = Pipeline::new(reg);
        let ctx = Context {
            session_id: "test".into(),
            trace_id: "test".into(),
            messages: vec![],
            tool_calls: vec![],
            tool_results: vec![],
            terminated: false,
            extras: std::collections::HashMap::new(),
        };

        let ctx = pipeline.invoke("tool-execute.before", ctx).await.unwrap();
        assert!(ctx.terminated);
    }

    struct BlockerHandler;
    #[async_trait::async_trait]
    impl Handler for BlockerHandler {
        async fn invoke(&self, mut ctx: Context) -> Result<Context> {
            ctx.terminated = true;
            Ok(ctx)
        }
    }

    struct ShouldNotRunHandler;
    #[async_trait::async_trait]
    impl Handler for ShouldNotRunHandler {
        async fn invoke(&self, _ctx: Context) -> Result<Context> {
            panic!("should not be called");
        }
    }
}
