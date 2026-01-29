# Agent-BE: High-Availability AI Agent Backend

Agent-BE is a robust, high-availability backend infrastructure for AI Agents, leveraging a polyglot microservice architecture with **Go (gRPC-Gateway)** and **Python (gRPC Server)**.

## Key Features

- **Polyglot Power**: Combines Go's efficiency for the API gateway and Python's versatility for AI/ML and business logic.
- **gRPC Native**: High-performance communication between services using Protobuf.
- **RESTful API**: Seamlessly exposes gRPC services as RESTful endpoints via gRPC-Gateway.
- **Session Management**: Automated database session and transaction management in Python.
- **Extensible Architecture**: Layered design for easy expansion of models, CRUD, and services.

## Technology Stack

- **Gateway**: Go v1.25+ with [gRPC-Gateway](https://github.com/grpc-ecosystem/grpc-gateway).
- **Backend Service**: Python v3.10+ with [gRPC](https://grpc.io/).
- **Database**: PostgreSQL with SQLAlchemy ORM.
- **Deployment**: Docker & Makefile orchestration.

## Quick Start

For detailed setup and usage instructions, please refer to:
- [**User Guide (Chinese)**](doc/USAGE.md)
- [**Developer Extension Guide (Chinese)**](doc/EXTENSION.md)

### Basic Commands

```bash
# Start the database
make pgsql-start

# Build and start all services
make start

# Cleanup
make clean
```

## License

[MIT License](LICENSE)
