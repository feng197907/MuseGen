# MuseGen GPU 云服务器 SSH 端口转发
# AutoDL RTX 5090 32G — connect.westb.seetacloud.com:20262
#
# 转发端口:
#   11434 → Ollama (qwen3:14b)
#   8188  → ComfyUI (SDXL + IP-Adapter + AnimateDiff)
#   5000  → CosyVoice (CosyVoice-300M-SFT)

$sshHost = "connect.westb.seetacloud.com"
$sshPort = 20262
$sshUser = "root"
$sshPass = "j8Fo01AP/2cP"

Write-Host "正在建立 SSH 隧道到 AutoDL GPU 服务器..." -ForegroundColor Cyan
Write-Host "  Ollama      : localhost:11434 → 远程:11434" -ForegroundColor Green
Write-Host "  ComfyUI     : localhost:8188  → 远程:8188" -ForegroundColor Green
Write-Host "  CosyVoice   : localhost:5000  → 远程:5000" -ForegroundColor Green
Write-Host "按 Ctrl+C 断开隧道" -ForegroundColor Yellow
Write-Host ""

ssh -o StrictHostKeyChecking=no `
    -p $sshPort `
    -L 11434:127.0.0.1:11434 `
    -L 8188:127.0.0.1:8188 `
    -L 5000:127.0.0.1:5000 `
    "${sshUser}@${sshHost}"
（内容由AI生成，仅供参考）
