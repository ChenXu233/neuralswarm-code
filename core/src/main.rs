use clap::Parser;
use anyhow::Result;
use tracing_subscriber;

mod config;
mod connection;
mod executor;

#[derive(Parser)]
#[command(name = "neuralswarm-client")]
#[command(about = "NeuralSwarm Client Core")]
struct Args {
    #[arg(long)]
    server: String,

    #[arg(long)]
    token: String,

    #[arg(long)]
    name: Option<String>,
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt::init();

    let args = Args::parse();
    let config = config::Config::from_args(args.server, args.token, args.name);

    connection::run(config).await
}
