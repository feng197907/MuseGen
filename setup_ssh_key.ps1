# One-time: Copy SSH public key to GPU server
# Run this once so ssh_tunnel.ps1 can use key-based auth (no password prompt)

$sshKey = "$env:USERPROFILE\.ssh\musegen_autodl"

if (-not (Test-Path $sshKey)) {
    Write-Host "[>>] Generating SSH key..." -ForegroundColor Cyan
    ssh-keygen -t ed25519 -f $sshKey -N '""' -q
    Write-Host "[OK] Key generated: $sshKey" -ForegroundColor Green
}

Write-Host "[>>] Copying public key to GPU server..." -ForegroundColor Cyan
Write-Host "     Password: j8Fo01AP/2cP" -ForegroundColor Yellow
Write-Host ""

Get-Content -Encoding UTF8 "$sshKey.pub" | ssh -o StrictHostKeyChecking=no -p 44400 root@connect.westb.seetacloud.com "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys && echo OK: Key installed"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SSH key setup complete!" -ForegroundColor Green
    Write-Host "  ssh_tunnel.ps1 will now use key auth" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[ERROR] Failed to copy key. Check password and server connectivity." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
