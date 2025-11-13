.PHONY: build up down test clean security-check security-scan

# Build the container
build:
	docker-compose build

# Start containers
up:
	docker-compose up -d

# Stop containers
down:
	docker-compose down

# Run tests
test:
	python -m pytest tests/ -v

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Security scan
security-scan:
	@echo "Running security scans..."
	@if command -v hadolint >/dev/null 2>&1; then \
		hadolint Dockerfile; \
	else \
		echo "Hadolint not installed, skipping..."; \
	fi
	@echo "Container security checks:"
	@if docker ps | grep -q secure-app; then \
		echo "  - Non-root user: $$(docker exec secure-app whoami 2>/dev/null)"; \
		echo "  - User ID: $$(docker exec secure-app id -u 2>/dev/null)"; \
		echo "  - Health status: $$(docker inspect secure-app --format '{{.State.Health.Status}}' 2>/dev/null)"; \
	else \
		echo "  Container 'secure-app' is not running"; \
	fi

# Check container security
security-check:
	@chmod +x scripts/security-scan.sh
	@./scripts/security-scan.sh

# View logs
logs:
	docker-compose logs -f

# Windows run script
win-run:
	powershell -File scripts/run-container.ps1
