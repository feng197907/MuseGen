# MuseGen — AI 动漫视频生成系统

将故事文本自动转化为精美的动漫视频，由 AI 驱动的全流程创作平台。

## 系统架构

MuseGen 采用前后端分离架构，通过 6 步 AI 流水线将故事文本转化为动漫视频：

1. **故事解析** — LLM (GPT-4o) 解析故事文本，提取角色、场景和分镜
2. **资产生成** — SDXL 生成角色立绘和场景图
3. **关键帧生成** — SDXL + IP-Adapter 保持角色一致性合成关键帧
4. **动画生成** — SVD (Stable Video Diffusion) 图生视频
5. **配音生成** — ElevenLabs / 火山引擎 TTS 配音
6. **视频合成** — FFmpeg 多轨合成 + 字幕

前端通过 SSE (Server-Sent Events) 实时接收任务进度。

## 技术栈

### 前端
- Vite 5 + React 18 + TypeScript
- MUI v5 + Tailwind CSS
- Zustand + Immer (全局状态 + 撤销/重做)
- TanStack React Query (服务端状态)
- @dnd-kit (拖拽排序)
- WaveSurfer.js (音频波形)

### 后端
- Python 3.11 + FastAPI
- Celery 5 + Redis (异步任务队列)
- SQLAlchemy 2.0 (async) + PostgreSQL
- MinIO / S3 对象存储
- FFmpeg 视频合成

### AI 服务
- OpenAI GPT-4o (故事解析)
- Replicate SDXL + IP-Adapter (图像生成)
- Replicate SVD (视频生成)
- ElevenLabs / 火山引擎 (TTS)

## 快速开始

### 前提条件
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 API Key 等配置
```

### 2. 使用 Docker Compose 启动

```bash
docker compose up -d
```

服务启动后：
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- MinIO 控制台: http://localhost:9001

### 3. 本地开发（不用 Docker）

**后端：**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Celery Worker：**
```bash
cd backend
celery -A celery_worker worker --loglevel=info --concurrency=2
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看交互式 API 文档。

主要端点：

| Method | Path | 说明 |
|--------|------|------|
| POST | `/api/v1/projects` | 创建项目 |
| GET | `/api/v1/projects` | 获取项目列表 |
| POST | `/api/v1/generate/full-pipeline` | 一键全流程生成 |
| GET | `/api/v1/sse/tasks/{task_id}` | SSE 实时进度推送 |

## 项目结构

```
MuseGen/
├── frontend/          # Vite + React 前端
├── backend/           # FastAPI + Celery 后端
├── docker-compose.yml # 开发环境编排
└── .env.example       # 环境变量模板
```

## 许可证

MIT License
