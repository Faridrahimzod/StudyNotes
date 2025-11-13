Write-Host "=== Container Test Report ==="
Write-Host "Generated: $(Get-Date)"
Write-Host ""

# Build the image
Write-Host "1. Building Docker image..."
docker-compose build

# Start container
Write-Host "2. Starting container..."
docker-compose up -d

# Wait for container to start
Write-Host "3. Waiting for container to be ready..."
Start-Sleep -Seconds 30

# Check container status
Write-Host "4. Container status:"
docker-compose ps

# Check health status
Write-Host "5. Health check:"
$health_status = docker inspect secure-app --format '{{.State.Health.Status}}' 2>$null
if (-not $health_status) { $health_status = "unknown" }
Write-Host "   Health: $health_status"

# Check non-root user
Write-Host "6. Security checks:"
$user_id = docker exec secure-app id -u 2>$null
$user_name = docker exec secure-app whoami 2>$null
if (-not $user_id) { $user_id = "N/A" }
if (-not $user_name) { $user_name = "N/A" }
Write-Host "   User: $user_name (ID: $user_id)"

# Check image size
Write-Host "7. Image size:"
docker images | Select-String "secure-app"

Write-Host "8. Security scans:"
Write-Host "   - Note: Run security scans manually if needed"
Write-Host "     hadolint Dockerfile"
Write-Host "     docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --format table --severity HIGH,CRITICAL course-project-faridrahimzod-app:latest"

# Stop container
Write-Host "9. Cleaning up..."
docker-compose down

Write-Host ""
Write-Host "=== Test completed ==="
