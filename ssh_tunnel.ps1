# SSH tunnel to AutoDL GPU Server
# Forwards: Ollama, ComfyUI, CosyVoice

$sshHost = "connect.westb.seetacloud.com"
$sshPort = 44400
$sshUser = "root"
$sshKey = "$env:USERPROFILE\.ssh\musegen_autodl"

Write-Host "SSH tunnel to AutoDL GPU Server..." -ForegroundColor Cyan
Write-Host "  Ollama      localhost:11434" -ForegroundColor Green
Write-Host "  ComfyUI     localhost:8188" -ForegroundColor Green
Write-Host "  CosyVoice   localhost:5000" -ForegroundColor Green
Write-Host "Ctrl+C to disconnect" -ForegroundColor Yellow
Write-Host ""

if (Test-Path $sshKey) {
    Write-Host "Using SSH key: $sshKey" -ForegroundColor Gray
    ssh -o StrictHostKeyChecking=no `
        -i $sshKey `
        -p $sshPort `
        -L 11434:127.0.0.1:11434 `
        -L 8188:127.0.0.1:8188 `
        -L 5000:127.0.0.1:5000 `
        "${sshUser}@${sshHost}"
} else {
    Write-Host "[WARN] SSH key not found, using password auth" -ForegroundColor Yellow
    Write-Host "       Run: .\setup_ssh_key.ps1  to fix" -ForegroundColor Yellow
    ssh -o StrictHostKeyChecking=no `
        -p $sshPort `
        -L 11434:127.0.0.1:11434 `
        -L 8188:127.0.0.1:8188 `
        -L 5000:127.0.0.1:5000 `
        "${sshUser}@${sshHost}"
}
