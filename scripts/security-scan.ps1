Write-Host "=== Security Scan Report ==="
Write-Host "Generated: $(Get-Date)"
Write-Host ""

# Check if container is running and scan it
Write-Host "1. Container Security Checks:"
$containerRunning = docker ps | Select-String "secure-app"
if ($containerRunning) {
    Write-Host "   - Non-root user: $(docker exec secure-app whoami 2>$null)"
    Write-Host "   - User ID: $(docker exec secure-app id -u 2>$null)"
    Write-Host "   - Health status: $(docker inspect secure-app --format '{{.State.Health.Status}}' 2>$null)"
} else {
    Write-Host "   Container 'secure-app' is not running"
}
Write-Host ""

Write-Host "=== End of Security Scan ==="
