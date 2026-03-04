# 项目使用文档

> [!NOTE]
> **🤖 AI 生成声明**
> 本文档内容由 AI 自动生成并整理。在阅读和使用过程中，请结合实际项目情况进行人工复核。

本项目是一个高可用的 AI Agent 后端基础架构，采用 **Go (gRPC-Gateway) + Python (gRPC Server)** 的多语言微服务模式。

## 1. 环境准备

### 软件依赖
- **Go**: v1.25+
- **Python**: v3.10+
- **Docker**: 用于运行 PostgreSQL 数据库
- **Buf**: 用于 Protobuf 代码生成

### 环境变量配置
项目支持通过环境变量动态配置（默认值为本地开发配置）：
- `GRPC_SERVER_ADDR`: Python gRPC 服务地址（默认 `localhost:50051`）
- `GATEWAY_ADDR`: Go HTTP 网关地址（默认 `:8080`）
- `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD`: 数据库连接配置

## Quick Start

1. Start background services:

```bash
# 使用 Makefile 启动容器化 PostgreSQL
make pgsql-start
```

2. Initialize environment and start all services:

```bash
# 安装依赖、生成代码并启动所有服务
make start
```

3. Wait for services to be ready:

- gRPC Gateway: `http://localhost:8080`
- Python gRPC: `localhost:50051`
- PostgreSQL: `localhost:5432`

1. Verify service status:
- **健康检查**: 访问 `http://localhost:8080/health`
- **查看日志**: 检查终端输出或 `logs/` 目录

## API Usage Examples

### Create Construction Progress

```bash
curl -X POST http://localhost:8080/api/v1/construction/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "某写字楼施工计划",
    "plan_type": 2,
    "creator": "admin"
  }'
```

### List by Page

```bash
curl -X POST http://localhost:8080/api/v1/construction/progress \
  -H "Content-Type: application/json" \
  -d '{
    "page": 1,
    "page_size": 10
  }'
```

## 4. 常见问题排查
- **连接失败**: 确保 Docker 守护进程已启动且 5432 端口未被占用。
- **编译错误**: 检查是否安装了 `protoc-gen-go` 和 `protoc-gen-grpc-gateway` 插件。
