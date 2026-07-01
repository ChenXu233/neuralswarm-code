mod kernel;
mod plugins;
mod server;

use std::sync::Arc;
use clap::Parser;

#[derive(Parser)]
#[command(name = "neuralswarm")]
struct Args {
    /// 项目路径（工作区挂载点）
    #[arg(default_value = ".")]
    path: String,

    /// 监听端口
    #[arg(long, default_value = "8080")]
    port: u16,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();
    let args = Args::parse();

    // 1. 初始化工作区
    let mut workspace = kernel::workspace::Workspace::new();
    workspace.mount("project", std::path::PathBuf::from(&args.path));

    // 2. 初始化注册表
    let mut registry = kernel::registry::Registry::new();

    // 3. 注册所有内置插件
    plugins::register_all(&mut registry);

    // 4. 创建管道引擎
    let pipeline = Arc::new(kernel::pipeline::Pipeline::new(registry));

    // 5. 启动 HTTP 服务
    let state = Arc::new(server::AppState {
        pipeline,
        workspace,
    });

    let app = server::http::routes().with_state(state);
    let addr = format!("0.0.0.0:{}", args.port);

    tracing::info!("NeuralSwarm kernel starting on {}", addr);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
