# 百词斩 Web MVP（可运行原型）

这是一套「百词斩风格」背单词 Web MVP：

- **前端**：React + Vite + Tailwind v4 + shadcn/ui（项目名：baicizhan-web-mvp）
- **后端**：Python FastAPI + SQLAlchemy
- **数据库**：MySQL（本地可用 MySQL8 / MariaDB 代替）

本 MVP **只实现核心两块**：

1. **背单词做题**（四选一）
2. **单词详解**（释义 / 例句 / 词根）

> 说明：为了便于 AnyGen 预览环境，本后端默认 CORS 放开（`allow_origins=["*"]`）。生产环境请改为前端域名白名单。

---

## 目录结构

- `./backend/` FastAPI 后端
- `./docker-compose.yml`（可选）一键启动 MySQL + API（需要你本机有 Docker）
- 前端在：`/home/user/workspace/website/baicizhan-web-mvp/`

---

## 本地运行（推荐：Docker）

前提：安装 Docker Desktop 或 Docker Engine。

### 1）启动 MySQL + 后端 API

在本目录执行：

```bash
docker compose up -d --build
```

- MySQL：`localhost:3306`
- API：`http://localhost:8001`（容器内 8000 映射到宿主机 8001）

### 2）启动前端

```bash
cd /home/user/workspace/website/baicizhan-web-mvp
pnpm install
pnpm dev
```

访问：`http://localhost:5173`

---

## 本地运行（无 Docker：用系统 MySQL / MariaDB）

### 1）准备数据库

创建数据库与用户（示例）：

```sql
CREATE DATABASE IF NOT EXISTS baicizhan CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'bcz'@'localhost' IDENTIFIED BY 'bczpass';
GRANT ALL PRIVILEGES ON baicizhan.* TO 'bcz'@'localhost';
FLUSH PRIVILEGES;
```

### 2）启动后端

```bash
cd /home/user/workspace/baicizhan-mvp/backend
pip install -r requirements.txt

export DATABASE_URL='mysql+pymysql://bcz:bczpass@localhost:3306/baicizhan?charset=utf8mb4'
export SEED_ON_STARTUP=true

uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3）启动前端

```bash
cd /home/user/workspace/website/baicizhan-web-mvp
pnpm install
pnpm dev
```

---

## MVP 页面

- `/` 首页学习仪表盘（今日单词、剩余天数、进度条、开始按钮）
- `/study/:sessionId` 背单词做题页
- `/word/:id` 单词详解页

---

## API（后端）

- `GET /health`
- `GET /api/plan`
- `POST /api/session/start` → `{ session_id }`
- `GET /api/session/{session_id}/next` → 下一道题
- `POST /api/session/{session_id}/word/{word_id}/answer` → 提交答案
- `GET /api/words/{word_id}` → 单词详情

---

## 数据与种子词库

后端启动时会在数据库为空的情况下自动导入：

- `backend/data/seed_words.json`

你可以把它替换成更完整的词库（建议后续加词书/词库版本号）。
