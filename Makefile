WORKROOT := $(shell pwd)
INFO = \033[1;33m[INFO]: \033[0;36m
EINFO = \033[0m
BUF = $(if $(BUFTOKEN),BUF_TOKEN=$(BUFTOKEN) )buf

GO := $(shell command -v go 2>/dev/null || which go 2>/dev/null)

PYTHON_VENV_DIR ?= $(WORKROOT)/venv
PYTHON_BIN := $(PYTHON_VENV_DIR)/bin/python


pbgen: ## Generate protobuf files
	@echo -e "${INFO}generating protobuf files...${EINFO}"
	cd ${WORKROOT}/proto && ${BUF} dep update
	${BUF} generate
	${BUF} generate buf.build/envoyproxy/protoc-gen-validate

pgsql: ## Start a local PostgreSQL instance using Docker
	@echo -e "${INFO}starting PostgreSQL...${EINFO}"
	sh ./scripts/pgsql_start.sh

clean: ## Clean generated files
	@echo -e "${INFO}cleaning generated files...${EINFO}"
	@find . -name "*.pb.go" | xargs --no-run-if-empty rm
	@find . -name "*.pb.gw.go" | xargs --no-run-if-empty rm
	@find . -name "*.pb.validate.go" | xargs --no-run-if-empty rm
	@rm -rf ./agent/
	@rm -rf ./validate
	@rm -rf ./swagger
	@rm -rf ./logs

pgsql-clean: ## Stop and remove the local PostgreSQL Docker instance
	@echo -e "${INFO}stopping PostgreSQL...${EINFO}"
	docker rm -f postgres-prod

start: pbgen pgsql-clean pgsql
	@if [ ! -d $(PYTHON_VENV_DIR) ]; then \
		echo -e "${INFO}initializing python venv at $(PYTHON_VENV_DIR)...${EINFO}"; \
		mkdir -p $(dir $(PYTHON_VENV_DIR)); \
		python3 -m venv $(PYTHON_VENV_DIR); \
	else \
		echo -e "${INFO}using existing python venv at $(PYTHON_VENV_DIR)...${EINFO}"; \
	fi
	@echo -e "${INFO}activating python venv at $(PYTHON_VENV_DIR)...${EINFO}"
	@. $(PYTHON_VENV_DIR)/bin/activate; \
		pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple; \
		pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn; \
		time pip install -r requirements.txt || (echo "pip install failed"; exit 1);

	@mkdir -p ${WORKROOT}/logs
	@echo -e "${INFO}starting background service...${EINFO}"
	@nohup env PYTHONPATH=. ${PYTHON_BIN} src/services/service.py > ${WORKROOT}/logs/service.log 2>&1 &
	@${GO} run ${WORKROOT}/main.go

.PHONY: pbgen clean pgsql pgsql-clean start