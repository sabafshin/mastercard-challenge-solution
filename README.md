# MasterCard FCS DevOps Challenge - Complete Solution

## Quick Start

### **Prerequisites**
- Python 3.12+ (latest features required)
- Poetry (modern dependency management)
- Docker (optional, for containerized deployment)

### **Installation & Running**
```bash
# Setup environment
poetry install

# Run comprehensive test suite
poetry run pytest -v

# Start development server
poetry run python -m src.main
# Server: http://localhost:8000
```

### **API Usage Examples**
```bash
# Create account (server assigns ID) - RESTful approach
curl -X POST http://localhost:8000/accounts \
  -H "Content-Type: application/json" \
  -d '{"name": "Enterprise Account", "balance": 10000.00}'

# List accounts with filtering
curl "http://localhost:8000/accounts?active_only=true"

# Partial update (PATCH) - efficient updates
curl -X PATCH http://localhost:8000/accounts/1 \
  -H "Content-Type: application/json" \
  -d '{"balance": 15000.00}'

# Health check for monitoring
curl http://localhost:8000/health
```

### **Interactive API Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## 🧪 Testing Excellence

### **Test Metrics**
```bash
poetry run pytest -v
```

## Docker Deployment

```bash
# Multi-environment support
docker-compose up dev        # Development with hot reload
docker-compose up production # Production-optimized build
docker-compose up base-image # Custom base image creation
```

## Complete Package Structure

```
mastercard-challenge-solution/
├── docker
│   ├── Dockerfile.base
│   ├── Dockerfile.dev
│   └── Dockerfile.prod
├── src
│   ├── dependencies
│   │   ├── __init__.py
│   │   └── repository.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── account.py
│   │   └── health.py
│   ├── repositories
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── memory.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── accounts.py
│   │   └── health.py
│   ├── __init__.py
│   ├── main.py
│   └── original.main.py
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_essential.py
│   ├── test_repository.py
│   └── test_repository_factory.py
├── docs
│   ├── API_SPECIFICATION.md
│   ├── Notes.md
│   └── api_spec.json
├── README.md
├── docker-compose.yml
└── pyproject.toml
```
