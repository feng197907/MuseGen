# SSH tunnel to Tencent Cloud Server (MinIO only)
# Forwards MinIO API :9000 and Console :9001

$sshHost = "你的腾讯云IP"      # <-- 改成实际IP
$sshPort = 22
$sshUser = "root"

Write-Host "SSH tunnel to Tencent Cloud..." -ForegroundColor Cyan
Write-Host "  MinIO API   localhost:9000" -ForegroundColor Green
Write-Host "  MinIO Web   localhost:9001" -ForegroundColor Green
Write-Host "Ctrl+C to disconnect" -ForegroundColor Yellow

ssh -o StrictHostKeyChecking=no `
    -p $sshPort `
    -L 9000:127.0.0.1:9000 `
    -L 9001:127.0.0.1:9001 `
    "${sshUser}@${sshHost}"
