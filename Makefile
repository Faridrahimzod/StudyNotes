.PHONY: build up down test clean scan

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
	docker-compose exec app python -m pytest tests/ -v

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Security scan (if hadolint is available)
scan:
	docker run --rm -i hadolint/hadolint < Dockerfile

# Check container health
health:
	docker inspect secure-app --format "{{.State.Health.Status}}"

# View logs
logs:
	docker-compose logs -f

# Run specific script for Windows
win-run:
	powershell -File scripts/run-container.ps1
