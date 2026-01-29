WORKROOT := $(shell pwd)
PYTHON_VENV_DIR ?= $(WORKROOT)/venv
PYTHON_BIN := $(PYTHON_VENV_DIR)/bin/python
GO := $(shell command -v go 2>/dev/null || which go 2>/dev/null)
BUF = $(if $(BUFTOKEN),BUF_TOKEN=$(BUFTOKEN) )buf

# 颜色定义
YELLOW = \033[1;33m
CYAN = \033[0;36m
RESET = \033[0m
INFO = $(YELLOW)[INFO]: $(CYAN)
EINFO = $(RESET)

.DEFAULT_GOAL := help

help: ## 显示帮助信息 (Default)
	@echo -e "用法: make \033[36m<目标>\033[0m"
	@echo -e "\n\033[1m可用目标:\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## 初始化 Python 虚拟环境
	@if [ ! -d $(PYTHON_VENV_DIR) ]; then \
		echo -e "${INFO}初始化 python venv 于 $(PYTHON_VENV_DIR)...${EINFO}"; \
		python3 -m venv $(PYTHON_VENV_DIR); \
	fi

install: venv ## 安装 Python 项目依赖
	@echo -e "${INFO}激活 venv 并安装依赖...${EINFO}"
	@. $(PYTHON_VENV_DIR)/bin/activate; \
		time pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt || (echo "pip install 失败"; exit 1);

pbgen: ## 生成基于 Protobuf 的多语言代码 (Go/Python/Swagger)
	@echo -e "${INFO}正在尝试更新依赖并生成代码...${EINFO}"
	@cd ${WORKROOT}/proto && ${BUF} dep update || echo -e "${YELLOW}[WARN]: 远程依赖更新失败，尝试使用本地缓存...${RESET}"
	@${BUF} generate || (echo -e "${YELLOW}[ERROR]: 代码生成失败，请检查 buf 配置或本地环境${RESET}"; exit 1)
	@${BUF} generate buf.build/envoyproxy/protoc-gen-validate || echo -e "${YELLOW}[WARN]: PGV 远程插件生成失败${RESET}"

pgsql: ## 启动本地 PostgreSQL 容器
	@echo -e "${INFO}正在启动 PostgreSQL 容器...${EINFO}"
	@sh ./scripts/pgsql_start.sh

pgsql-clean: ## 停止并删除 PostgreSQL 容器产物
	@echo -e "${INFO}正在清理 PostgreSQL 容器...${EINFO}"
	@docker rm -f postgres-prod 2>/dev/null || true

clean: ## 清理所有生成的代码、日志及缓存文件
	@echo -e "${INFO}正在清理生成产物...${EINFO}"
	@find proto -name "*.pb.go" -delete 2>/dev/null || true
	@find proto -name "*.pb.gw.go" -delete 2>/dev/null || true
	@find proto -name "*.pb.validate.go" -delete 2>/dev/null || true
	@find proto -name "*_pb2.py" -delete 2>/dev/null || true
	@find proto -name "*_pb2_grpc.py" -delete 2>/dev/null || true
	@rm -rf ./proto/swagger ./logs
	@find . -name "__pycache__" -type d -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null || true

stop: ## 停止后台运行的 Python 服务及 Go 网关进程
	@echo -e "${INFO}正在停止服务进程...${EINFO}"
	@pkill -f "src/main.py" || true
	@lsof -ti:50051 | xargs kill -9 2>/dev/null || true
	@lsof -ti:8080 | xargs kill -9 2>/dev/null || true
	@echo -e "${INFO}所有旧进程已清理${EINFO}"

start: stop pbgen pgsql-clean pgsql install ## 一键初始化并启动所有服务 (后端+网关)
	@mkdir -p ${WORKROOT}/logs
	@echo -e "${INFO}正在启动后台服务...${EINFO}"
	@nohup env PYTHONPATH=.:${WORKROOT}/proto ${PYTHON_BIN} src/main.py > ${WORKROOT}/logs/service.log 2>&1 &
	@echo -e "${INFO}正在启动 Go HTTP 网关...${EINFO}"
	@${GO} run ${WORKROOT}/main.go

.PHONY: help venv install pbgen pgsql pgsql-clean clean stop start