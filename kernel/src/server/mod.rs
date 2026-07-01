pub mod http;
pub mod ws;

use std::sync::Arc;
use crate::kernel::pipeline::Pipeline;
use crate::kernel::workspace::Workspace;
use crate::storage::session_store::SessionStore;

pub struct AppState {
    pub pipeline: Arc<Pipeline>,
    pub workspace: Workspace,
    pub store: SessionStore,
}
