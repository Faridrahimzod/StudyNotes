#!/bin/bash

echo "=== Security Scan Report ==="
echo "Generated: $(date)"
echo

# Scan Dockerfile with hadolint
echo "1. Dockerfile Lint (Hadolint):"
if command -v hadolint &> /dev/null; then
    hadolint Dockerfile
else
    echo "Hadolint not installed, skipping..."
fi
echo

# Check if container is running and scan it
echo "2. Container Security Checks:"
if docker ps | grep -q secure-app; then
    echo "   - Non-root user: $(docker exec secure-app whoami 2>/dev/null || echo 'Container not running')"
    echo "   - User ID: $(docker exec secure-app id -u 2>/dev/null || echo 'N/A')"
    echo "   - Health status: $(docker inspect secure-app --format '{{.State.Health.Status}}' 2>/dev/null || echo 'N/A')"
else
    echo "   Container 'secure-app' is not running"
fi
echo

echo "=== End of Security Scan ==="
