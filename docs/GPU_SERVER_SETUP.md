# GPU 服务器部署指南（AutoDL）

## 1. 租用实例

| 配置项 | 推荐值 |
|--------|--------|
| 平台 | [AutoDL](https://www.autodl.com) |
| 显卡 | RTX 4090（24G 显存）约 ¥2/小时 |
| 镜像 | PyTorch 2.0+ / CUDA 11.8+ |
| 存储 | 系统盘 50GB 免费，建议加 100GB 数据盘（¥3/天） |

创建实例后，在控制台获得：
- 公网 SSH 地址和端口
- JupyterLab / Web SSH 入口

---

## 2. 连接到服务器

用 AutoDL 自带的 Web SSH（最简单），或本地终端：

```bash
ssh -p <SSH端口> root@<公网IP>
```

---

## 3. 安装 Ollama（LLM 大语言模型）

```bash
# 安装
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型（14B 通用能力强，8B 省显存）
ollama pull qwen3:14b

# 测试
ollama run qwen3:14b "你好，请用JSON格式解析这句话：一个少年在雨中奔跑"
```

Ollama 启动后自动监听 11434 端口，OpenAI 兼容 API 地址为 `http://localhost:11434/v1`。

---

## 4. 安装 ComfyUI（图像 + 视频生成）

### 4.1 安装主体

```bash
cd /root
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

### 4.2 下载 SDXL 模型（生图用）

```bash
cd models/checkpoints

# 动漫风格推荐（二选一）：
# Animagine XL v3.1（日系动漫，推荐）
wget -O animagineXL_v31.safetensors https://huggingface.co/cagliostrolab/animagine-xl-3.1/resolve/main/animagine-xl-3.1.safetensors

# 或者 Dreamshaper XL（通用风格）
wget -O dreamshaperXL_v21.safetensors https://huggingface.co/Lykon/dreamshaper-xl-v2-turbo/resolve/main/DreamShaperXL_Turbo_v2_1.safetensors
```

### 4.3 安装 IP-Adapter 插件（角色一致性）

```bash
cd custom_nodes
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
cd ComfyUI_IPAdapter_plus
pip install -r requirements.txt

# 下载 IP-Adapter 模型文件到 ComfyUI/models/ipadapter/
mkdir -p ../../models/ipadapter
cd ../../models/ipadapter
wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors
```

### 4.4 安装 AnimateDiff 插件（图生视频）

```bash
cd ../../
cd custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
cd ComfyUI-AnimateDiff-Evolved
pip install -r requirements.txt

# 下载 AnimateDiff 运动模块
mkdir -p ../../models/animatediff_models
cd ../../models/animatediff_models
wget https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt
```

### 4.5 启动 ComfyUI

```bash
cd /root/ComfyUI
python main.py --port 8188 --listen 0.0.0.0
```

访问 `http://<公网IP>:8188` 确认界面能打开。

---

## 5. 安装 CosyVoice（语音合成）

```bash
cd /root
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice
pip install -r requirements.txt

# 下载预训练模型
python tools/download_models.py
```

CosyVoice 默认不带 REST API，需要额外安装服务层：

```bash
pip install fastapi uvicorn

# 创建 API 服务文件 api_server.py（内容见下方）
```

`api_server.py` 内容：

```python
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import base64
from cosyvoice.cli.cosyvoice import CosyVoice
from cosyvoice.utils.file_utils import load_wav
import torch
import tempfile
import os

app = FastAPI()
cosyvoice = CosyVoice("pretrained_models/CosyVoice-300M-SFT")

class TTSRequest(BaseModel):
    text: str
    voice: str = "default"
    speed: float = 1.0

@app.post("/tts")
async def tts(req: TTSRequest):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        output_path = f.name
    cosyvoice.inference_sft(req.text, "中文女", output_path)
    with open(output_path, "rb") as f:
        audio = f.read()
    os.unlink(output_path)
    b64 = base64.b64encode(audio).decode()
    return {"audio_base64": b64, "format": "wav"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

启动：

```bash
cd /root/CosyVoice
python api_server.py &
```

---

## 6. 全部启动（开机脚本）

创建 `/root/start_all.sh`：

```bash
#!/bin/bash
# MuseGen GPU 服务一键启动

echo "=== 启动 Ollama（端口 11434）==="
ollama serve &
sleep 3

echo "=== 启动 ComfyUI（端口 8188）==="
cd /root/ComfyUI && python main.py --port 8188 --listen 0.0.0.0 &
sleep 5

echo "=== 启动 CosyVoice（端口 5000）==="
cd /root/CosyVoice && python api_server.py &

echo "=== 全部启动完成 ==="
echo "Ollama:    http://localhost:11434"
echo "ComfyUI:   http://localhost:8188"
echo "CosyVoice: http://localhost:5000"
```

```bash
chmod +x /root/start_all.sh
```

---

## 7. AutoDL 端口转发

AutoDL 控制台 → 实例 → 自定义服务：

| 服务 | 内部端口 | 说明 |
|------|---------|------|
| Ollama | 11434 | LLM OpenAI 兼容 API |
| ComfyUI | 8188 | 图像生成 / 视频生成 |
| CosyVoice | 5000 | 语音合成 |

转发后获得公网 URL，填入 MuseGen `.env` 中的 `GPU_SERVER_HOST` 即可。

---

## 8. 验证服务

```bash
# 测试 Ollama
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3:14b","messages":[{"role":"user","content":"hello"}]}'

# 测试 CosyVoice
curl -X POST http://localhost:5000/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"你好世界","voice":"default"}'
```

---

## 9. 省钱技巧

- **不用时关机**：关机后 GPU 不计费，只收存储费（约 ¥0.03/GB/天）
- **学生认证**：享 85 折
- **保存镜像**：环境配好后保存为私有镜像，下次租用直接加载，无需重新安装