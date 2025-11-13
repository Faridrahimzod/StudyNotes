# Container Deployment Guide

## Local Development with Docker

### Prerequisites
- Docker
- Docker Compose

### Quick Start

```bash
# Build and start the container
docker-compose up --build -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f app

# Run full container test
make container-test

# Or on Windows PowerShell
make container-test-win
```

### Manual Testing Commands

```bash
# Build image
docker-compose build

# Start container
docker-compose up -d

# Check health status
docker inspect secure-app --format '{{.State.Health.Status}}'

# Check non-root user
docker exec secure-app whoami
docker exec secure-app id -u

# Check container logs
docker-compose logs app

# Stop container
docker-compose down
```

### Security Scanning
```bash
# Dockerfile linting (install hadolint first)
hadolint Dockerfile

# Vulnerability scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy:latest image \
    --format table \
    --severity HIGH,CRITICAL \
    course-project-faridrahimzod-app:latest
```

### Makefile Commands
- make build - Build container
- make up - Start containers
- make down - Stop containers
- make test - Run application tests
- make container-test - Run full container test (Linux/Mac)
- make container-test-win - Run container test (Windows)
- make security-scan - Run security scans
- make logs - View container logs

### Security Features
✅ Non-root user inside container

✅ Health checks

✅ Multi-stage build

✅ Minimal base image (python:3.12-slim)

✅ Security scanning ready
