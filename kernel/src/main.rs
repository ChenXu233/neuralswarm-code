mod config;
mod kernel;
mod plugins;
mod server;
mod storage;

use std::sync::Arc;
use clap::Parser;
use tower_http::cors::CorsLayer;

#[derive(Parser)]
#[command(name = "neuralswarm")]
struct Args {
    /// 配置文件路径
    #[arg(long, default_value = "neuralswarm.yaml")]
    config_file: String,

    /// 项目路径（覆盖配置文件，可选）
    #[arg(default_value = ".")]
    path: String,

    /// 监听端口（覆盖配置文件）
    #[arg(long)]
    port: Option<u16>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();
    let args = Args::parse();

    // 1. 加载配置
    let mut cfg = config::Config::from_file(&args.config_file)?;

    // 2. CLI 参数覆盖
    if args.port.is_some() {
        cfg.node.get_or_insert_with(|| config::NodeConfig { name: None, port: None }).port = args.port;
    }
    config::init(cfg);

    // 3. 初始化存储
    let store = storage::session_store::SessionStore::new("data/neuralswarm.db")?;
    tracing::info!("Storage initialized (data/neuralswarm.db)");

    // 4. 初始化注册表
    let mut registry = kernel::registry::Registry::new();

    // 5. 注册所有内置插件
    plugins::register_all(&mut registry);

    // 6. 创建管道引擎
    let pipeline = Arc::new(kernel::pipeline::Pipeline::new(registry));

    // 7. 为 LLM handler 注入 pipeline 引用
    plugins::llm::set_pipeline(pipeline.clone());

    // 8. 创建 WSS 管理器
    let wss_manager = Arc::new(server::ws::WssManager::new());

    // 为 LLM handler 注入 WSS 管理器
    plugins::llm::set_wss_manager(wss_manager.clone());

    // 9. 启动 HTTP 服务
    let state = Arc::new(server::AppState {
        pipeline,
        store,
        wss_manager,
        default_workspace_path: args.path,
    });

    let cors = CorsLayer::permissive();
    let app = server::http::routes()
        .merge(server::ws::ws_routes())
        .with_state(state)
        .layer(cors);
    let port = config::get().node.as_ref()
        .and_then(|n| n.port)
        .unwrap_or(8080);
    let addr = format!("0.0.0.0:{}", port);

    tracing::info!("NeuralSwarm kernel starting on {}", addr);
    tracing::info!("Config loaded from: {}", args.config_file);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}