# MuseGen Dev Stopper

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $rootDir

Write-Host "--- Stopping MuseGen Services ---" -ForegroundColor Cyan

# Stop Docker infrastructure
Write-Host "[>>] Stopping Docker services..." -ForegroundColor White
docker compose down 2>&1 | Out-Null
Write-Host "[OK] Docker (PostgreSQL, Redis, MinIO) stopped" -ForegroundColor Green

# Stop SSH tunnel processes
Write-Host "[>>] Closing SSH tunnels..." -ForegroundColor White
$sshProcesses = Get-Process ssh -ErrorAction SilentlyContinue
if ($sshProcesses) {
    $sshProcesses | Stop-Process -Force
    Write-Host "[OK] SSH tunnels closed" -ForegroundColor Green
} else {
    Write-Host "     No active SSH tunnels found" -ForegroundColor Gray
}

# Reminder
Write-Host ""
Write-Host "Please manually close these windows:" -ForegroundColor Yellow
Write-Host "  - Backend API (uvicorn)" -ForegroundColor White
Write-Host "  - Celery Worker" -ForegroundColor White
Write-Host "  - Frontend Vite" -ForegroundColor White
Write-Host "  - SSH Tunnel" -ForegroundColor White
Write-Host ""
Write-Host "[OK] Infrastructure cleaned up" -ForegroundColor Green
