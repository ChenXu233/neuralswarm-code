pub mod http;
pub mod ws;

use std::sync::Arc;
use crate::kernel::pipeline::Pipeline;
use crate::storage::session_store::SessionStore;

pub struct AppState {
    pub pipeline: Arc<Pipeline>,
    pub store: SessionStore,
    pub wss_manager: Arc<ws::WssManager>,
    pub default_workspace_path: String,
}
