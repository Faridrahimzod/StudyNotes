#!/bin/bash

echo "=== Container Test Report ==="
echo "Generated: $(date)"
echo

# Build the image
echo "1. Building Docker image..."
docker-compose build

# Start container
echo "2. Starting container..."
docker-compose up -d

# Wait for container to start
echo "3. Waiting for container to be ready..."
sleep 30

# Check container status
echo "4. Container status:"
docker-compose ps

# Check health status
echo "5. Health check:"
health_status=$(docker inspect secure-app --format '{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
echo "   Health: $health_status"

# Check non-root user
echo "6. Security checks:"
user_id=$(docker exec secure-app id -u 2>/dev/null || echo "N/A")
user_name=$(docker exec secure-app whoami 2>/dev/null || echo "N/A")
echo "   User: $user_name (ID: $user_id)"

# Check image size
echo "7. Image size:"
docker images | grep secure-app

# Run security scans if tools are available
echo "8. Security scans:"
if command -v hadolint &> /dev/null; then
    echo "   - Hadolint:"
    hadolint Dockerfile
else
    echo "   - Hadolint: not installed (skip)"
fi

if docker run --rm aquasec/trivy:latest version &> /dev/null; then
    echo "   - Trivy scan:"
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy:latest image \
        --format table \
        --severity HIGH,CRITICAL \
        course-project-faridrahimzod-app:latest
else
    echo "   - Trivy: not available (skip)"
fi

# Stop container
echo "9. Cleaning up..."
docker-compose down

echo
echo "=== Test completed ==="
