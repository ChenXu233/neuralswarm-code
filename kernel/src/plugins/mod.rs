pub mod llm;
pub mod file_ops;
pub mod shell;

use crate::kernel::registry::Registry;

pub fn register_all(registry: &mut Registry) {
    llm::register_handler(registry);
    file_ops::register(registry);
    shell::register(registry);
}
