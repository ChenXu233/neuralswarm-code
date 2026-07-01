mod config;
mod kernel;
mod plugins;
mod server;
mod storage;

use std::sync::Arc;
use clap::Parser;

#[derive(Parser)]
#[command(name = "neuralswarm")]
struct Args {
    /// 配置文件路径
    #[arg(long, default_value = "neuralswarm.yaml")]
    config: String,

    /// 项目路径（覆盖配置文件）
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
    let mut cfg = config::Config::from_file(&args.config)?;

    // 2. CLI 参数覆盖配置文件
    let port = args.port
        .or_else(|| cfg.node.as_ref().and_then(|n| n.port))
        .unwrap_or(8080);

    // 3. 初始化全局配置，确保 CLI 参数优先
    if args.port.is_some() {
        cfg.node.get_or_insert_with(|| config::NodeConfig { name: None, port: None }).port = args.port;
    }
    config::init(cfg);

    // 4. 初始化工作区
    let mut workspace = kernel::workspace::Workspace::new();
    workspace.mount("project", std::path::PathBuf::from(&args.path));
    // 如果有配置文件中的 mounts，也加上
    if let Some(ref ws_cfg) = config::get().workspace {
        if let Some(ref mounts) = ws_cfg.mounts {
            for m in mounts {
                if m.name != "project" {  // 避免重复
                    workspace.mount(&m.name, m.path.clone());
                }
            }
        }
    }

    // 5. 初始化注册表
    let mut registry = kernel::registry::Registry::new();

    // 6. 注册所有内置插件
    plugins::register_all(&mut registry);

    // 7. 创建管道引擎
    let pipeline = Arc::new(kernel::pipeline::Pipeline::new(registry));

    // 8. 为 LLM handler 注入 pipeline 引用
    plugins::llm::set_pipeline(pipeline.clone());

    // 9. 启动 HTTP 服务
    let state = Arc::new(server::AppState {
        pipeline,
        workspace,
    });

    let app = server::http::routes().with_state(state);
    let addr = format!("0.0.0.0:{}", port);

    tracing::info!("NeuralSwarm kernel starting on {}", addr);
    tracing::info!("Config loaded from: {}", args.config);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
