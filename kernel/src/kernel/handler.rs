use async_trait::async_trait;
use crate::kernel::context::Context;
use anyhow::Result;

/// 插件的唯一扩展契约。
/// 挂到某个点上，流到达时被管道引擎调用。
#[async_trait]
pub trait Handler: Send + Sync {
    async fn invoke(&self, ctx: Context) -> Result<Context>;
}
