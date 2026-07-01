# NeuralSwarm v2.0 — 多阶段构建
#
# 两种部署模式（通过 BUILD_PROFILE 控制）:
#   BUILD_PROFILE=user     → 用户神经元（内核 + UI）
#   BUILD_PROFILE=compute  → 计算神经元（仅内核，无 UI）
#
# 用法:
#   docker build --build-arg BUILD_PROFILE=user -t neuralswarm:user .
#   docker build --build-arg BUILD_PROFILE=compute -t neuralswarm:compute .

# === Stage 1: Rust 内核（通用） ===
FROM rust:1.80-alpine AS kernel-builder

RUN apk add --no-cache musl-dev protobuf-dev

WORKDIR /build
COPY kernel/ .

RUN cargo build --release --target x86_64-unknown-linux-musl

# === Stage 2: Vue 前端（仅 user profile） ===
FROM node:20-alpine AS frontend-builder

WORKDIR /build
COPY client/ .

RUN npm ci && npm run build

# === Stage 3: 运行镜像 ===
FROM alpine:3.20 AS base

RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app

COPY --from=kernel-builder \
    /build/target/x86_64-unknown-linux-musl/release/neuralswarm \
    /app/neuralswarm

EXPOSE 8000
VOLUME ["/data"]

# ── 用户神经元（含 UI）───────────────────────
FROM base AS user
COPY --from=frontend-builder /build/dist/ /app/ui/
ENV NS_UI_DIR=/app/ui
CMD ["/app/neuralswarm"]

# ── 计算神经元（仅内核，无 UI）───────────────
FROM base AS compute
CMD ["/app/neuralswarm", "--headless"]
