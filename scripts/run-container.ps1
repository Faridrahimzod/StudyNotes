Write-Host "Building and starting containers..."
docker-compose up --build -d

Write-Host "Waiting for app to be healthy..."
$timeout = 60
$startTime = Get-Date

do {
    Start-Sleep -Seconds 2
    $healthStatus = docker inspect secure-app --format "{{.State.Health.Status}}" 2>$null
    Write-Host "Current status: $healthStatus"

    if ((Get-Date).Subtract($startTime).TotalSeconds -gt $timeout) {
        Write-Host "Timeout waiting for app to be healthy"
        exit 1
    }
} until ($healthStatus -eq "healthy")

Write-Host "App is healthy!"
Write-Host "Testing endpoint..."
curl -f http://localhost:8000/health
if ($LASTEXITCODE -ne 0) {
    Write-Host "Health check failed"
}
