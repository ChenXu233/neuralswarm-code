pub mod http;
pub mod ws;

use std::sync::Arc;
use crate::kernel::pipeline::Pipeline;
use crate::kernel::workspace::Workspace;

pub struct AppState {
    pub pipeline: Arc<Pipeline>,
    pub workspace: Workspace,
}
