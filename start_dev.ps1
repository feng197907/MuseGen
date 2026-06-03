# MuseGen Dev Launcher
param(
    [switch]$SkipDocker,
    [switch]$SkipTunnel,
    [switch]$SkipBackend,
    [switch]$SkipWorker,
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Continue"
$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $rootDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MuseGen - AI Anime Video Generator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------
# 1. Check .env
# -----------------------------------------------------------
if (-not (Test-Path "$rootDir\.env")) {
    Write-Host "[!] .env not found, copying from .env.example..." -ForegroundColor Yellow
    Copy-Item "$rootDir\.env.example" "$rootDir\.env"
    Write-Host "[OK] .env created, please edit GPU server config" -ForegroundColor Green
    Write-Host "     Press any key to continue, or Ctrl+C to edit .env first" -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# -----------------------------------------------------------
# 2. Docker: PostgreSQL + Redis + MinIO
# -----------------------------------------------------------
if (-not $SkipDocker) {
    Write-Host "--- Docker Infrastructure ---" -ForegroundColor Cyan
    $dockerCheck = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCheck) {
        Write-Host "[SKIP] Docker not installed, using local services" -ForegroundColor Yellow
    } else {
        Write-Host "[>>] Starting PostgreSQL + Redis + MinIO via Docker..." -ForegroundColor White
        docker compose up -d postgres redis minio 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[WARN] Docker compose failed" -ForegroundColor Yellow
        } else {
            Write-Host "[OK] PostgreSQL(5432), Redis(6379), MinIO(9000/9001) started" -ForegroundColor Green
        }
    }
    Write-Host ""
}

# -----------------------------------------------------------
# 3. SSH Tunnel to GPU Server
# -----------------------------------------------------------
if (-not $SkipTunnel) {
    Write-Host "--- SSH Tunnel (GPU Server) ---" -ForegroundColor Cyan
    if (Test-Path "$rootDir\ssh_tunnel.ps1") {
        Write-Host "[>>] Opening SSH tunnel to AutoDL..." -ForegroundColor White
        Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$rootDir\ssh_tunnel.ps1`"" -WindowStyle Normal
        Write-Host "     Ollama(11434) ComfyUI(8188) CosyVoice(5000)" -ForegroundColor Gray
    } else {
        Write-Host "[SKIP] ssh_tunnel.ps1 not found" -ForegroundColor Yellow
    }
    Write-Host ""
}

# -----------------------------------------------------------
# 4. Backend API (FastAPI + Uvicorn)
# -----------------------------------------------------------
if (-not $SkipBackend) {
    Write-Host "--- Backend API ---" -ForegroundColor Cyan
    $backendDir = "$rootDir\backend"
    $venvActivate = "$backendDir\venv\Scripts\Activate.ps1"

    if (-not (Test-Path $venvActivate)) {
        Write-Host "[>>] Creating Python venv..." -ForegroundColor White
        python -m venv "$backendDir\venv"
        Write-Host "[OK] venv created" -ForegroundColor Green
    }

    Write-Host "[>>] Opening FastAPI server in new window..." -ForegroundColor White
    $apiScript = @'
Write-Host "Activating venv..." -ForegroundColor Cyan
& "BACKENDDIR\venv\Scripts\Activate.ps1"
Write-Host "Installing / checking dependencies..." -ForegroundColor Cyan
pip install -r "BACKENDDIR\requirements.txt" -q
Set-Location "BACKENDDIR"
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Backend API  http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs     http://localhost:8000/docs" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
uvicorn main:app --reload --port 8000
'@
    $apiScript = $apiScript.Replace("BACKENDDIR", $backendDir)
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiScript -WindowStyle Normal
    Write-Host "[OK] Backend API window opened (port 8000)" -ForegroundColor Green
    Write-Host ""
}

# -----------------------------------------------------------
# 5. Celery Worker
# -----------------------------------------------------------
if (-not $SkipWorker) {
    Write-Host "--- Celery Worker ---" -ForegroundColor Cyan
    $backendDir = "$rootDir\backend"

    Write-Host "[>>] Opening Celery Worker in new window..." -ForegroundColor White
    Write-Host "     (waiting for pip install to finish...)" -ForegroundColor Gray
    Start-Sleep -Seconds 5
    $workerScript = @'
Write-Host "Activating venv..." -ForegroundColor Cyan
& "BACKENDDIR\venv\Scripts\Activate.ps1"
Write-Host "Installing / checking dependencies..." -ForegroundColor Cyan
pip install -r "BACKENDDIR\requirements.txt" -q
Set-Location "BACKENDDIR"
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Celery Worker started" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
celery -A celery_worker worker --loglevel=info --concurrency=2 --pool=solo
'@
    $workerScript = $workerScript.Replace("BACKENDDIR", $backendDir)
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $workerScript -WindowStyle Normal
    Write-Host "[OK] Celery Worker window opened (--pool=solo for Windows)" -ForegroundColor Green
    Write-Host ""
}

# -----------------------------------------------------------
# 6. Frontend (Vite + React)
# -----------------------------------------------------------
if (-not $SkipFrontend) {
    Write-Host "--- Frontend ---" -ForegroundColor Cyan
    $frontendDir = "$rootDir\frontend"

    if (-not (Test-Path "$frontendDir\node_modules")) {
        Write-Host "[>>] First run: installing frontend deps..." -ForegroundColor White
        Push-Location $frontendDir
        npm install
        Pop-Location
        Write-Host "[OK] npm install done" -ForegroundColor Green
    }

    Write-Host "[>>] Opening Vite dev server in new window..." -ForegroundColor White
    $frontendScript = @'
Set-Location "FRONTENDDIR"
Write-Host "Installing / checking dependencies..." -ForegroundColor Cyan
npm install --prefer-offline 2>$null
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Frontend  http://localhost:5173" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
npx vite --host
'@
    $frontendScript = $frontendScript.Replace("FRONTENDDIR", $frontendDir)
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal
    Write-Host "[OK] Frontend window opened (port 5173)" -ForegroundColor Green
    Write-Host ""
}

# -----------------------------------------------------------
# Done
# -----------------------------------------------------------
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All services launched!" -ForegroundColor Cyan
Write-Host "  Frontend   http://localhost:5173" -ForegroundColor Green
Write-Host "  Backend    http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs   http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  MinIO      http://localhost:9001" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stop: use stop_dev.ps1 or close windows" -ForegroundColor Yellow
