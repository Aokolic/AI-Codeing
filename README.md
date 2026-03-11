# ⚡ 后真相时代 — 信息甄别平台

> 多来源聚合 · 事件时间线追踪 · 三维可信度量化评估

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Tests](https://img.shields.io/badge/Tests-36%20passed-059669)](./frontend/tests)

---

## 📖 项目简介

**后真相时代**是一套面向新闻核实与信息甄别场景的全栈 Web 平台。系统围绕"舆论案例"构建，将同一事件的多方报道聚合为统一时间线，并通过权威性、时效性、交叉验证三个维度对每个事件节点打出可信度评分，帮助读者快速判断信息真实性。

### 核心功能

| 功能模块 | 描述 |
|---------|------|
| 🗂 案例管理 | 创建、检索、搜索热度排序的信息案例 |
| 📅 事件时间线 | 按时间轴展示案例内所有事件节点，支持时间范围过滤 |
| 🔍 三维可信度评估 | 权威性 · 时效性 · 交叉验证，综合评分 0-100 |
| 📡 数据源管理 | RSS/Atom/Scraper 采集源配置，支持 Cron 定时触发 |
| 📰 内置媒体采集 | 8 个主流媒体源零配置自动采集，每 30 分钟更新 |
| 🏷 标签分类 | 多维标签体系，案例交叉归类 |
| 🔐 管理后台 | JWT 鉴权，管理员专属数据源管理面板 |

---

## 🏗 技术栈

### 后端
- **FastAPI** 0.135 — 异步 REST API，自动生成 OpenAPI 文档
- **SQLAlchemy** 2.0 (async) + **aiosqlite** — 异步 ORM，生产可切换 PostgreSQL
- **Alembic** — 数据库版本迁移
- **Pydantic v2** + **pydantic-settings** — 数据校验与配置管理
- **python-jose** — JWT 令牌签发与验证
- **APScheduler** — 数据源定时采集任务
- **pytest** + **pytest-asyncio** — 单元测试与集成测试

### 前端
- **Vue 3.4** (Composition API + `<script setup>`)
- **TypeScript 5.3** (strict 模式，vue-tsc 零错误)
- **Vite 5** — 构建工具，内置 `/api` → 后端代理
- **Naive UI 2.38** — 组件库
- **Vue Router 4** — SPA 路由
- **Axios** — HTTP 客户端，JWT 拦截器自动注入
- **Day.js** — 时间格式化与相对时间
- **Vitest** + **@vue/test-utils** — 7 个测试文件，36 个测试用例全部通过

---

## 📂 目录结构

```
AI-Codeing/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # 路由层 (auth/cases/events/credibility/feeds/tags)
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── schemas/            # Pydantic 请求响应模式
│   │   ├── services/           # 业务逻辑层
│   │   ├── tasks/              # APScheduler 定时任务
│   │   ├── config.py           # pydantic-settings 配置
│   │   ├── database.py         # 异步数据库引擎
│   │   └── main.py             # FastAPI 应用入口
│   ├── alembic/                # 数据库迁移脚本
│   ├── scripts/
│   │   └── seed_data.py        # 种子数据（10 个真实案例）
│   ├── tests/                  # 后端测试套件
│   ├── .env                    # 环境变量（本地开发）
│   └── requirements.txt
│
└── frontend/                   # Vue 3 前端
    ├── src/
    │   ├── api/                # HTTP 模块 (cases/events/credibility/feeds/auth)
    │   ├── components/         # 通用组件
    │   │   ├── AppLayout.vue   # 全局导航布局
    │   │   ├── CaseCard.vue    # 案例卡片
    │   │   ├── CredibilityBadge.vue  # 可信度徽章
    │   │   ├── CredibilityPanel.vue  # 可信度详情面板
    │   │   ├── EventCard.vue   # 事件卡片（含可信度警告）
    │   │   ├── FeedStatusPanel.vue   # 数据源状态面板
    │   │   ├── SearchBar.vue   # 搜索栏
    │   │   └── Timeline.vue    # 事件时间线
    │   ├── composables/
    │   │   └── useTimeline.ts  # 时间线状态管理 composable
    │   ├── pages/
    │   │   ├── HomePage.vue        # 首页（Hero + 标签过滤 + 热度排行）
    │   │   ├── CaseDetailPage.vue  # 案例详情页 + 时间线 + 可信度抽屉
    │   │   ├── SearchResultPage.vue # 搜索结果页
    │   │   └── AdminPage.vue       # 管理后台（登录 + 数据源管理）
    │   ├── types/index.ts      # 所有 TypeScript 类型定义
    │   └── styles/main.css     # 全局样式 + CSS 变量
    └── tests/                  # Vitest 测试套件（36 个用例）
```

---

## 🚀 快速启动

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

### 1. 克隆仓库

```bash
git clone https://github.com/Aokolic/AI-Codeing.git
cd AI-Codeing
```

### 2. 启动后端

```powershell
# 创建 Python 虚拟环境
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
$env:PYTHONPATH = $PWD
.venv\Scripts\alembic upgrade head

# 写入种子数据（可选）
.venv\Scripts\python scripts/seed_data.py

# 启动开发服务器
.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

后端启动后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 3. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

前端访问：http://localhost:5173

> Vite 已配置代理，所有 `/api/*` 请求自动转发至 `http://localhost:8000`，无需任何跨域配置。

---

## 🔑 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `changeme123` |

> ⚠️ 仅用于本地开发，生产环境请修改 `backend/.env` 中的凭据和 `JWT_SECRET`。

---

## 🌐 API 端点

| 方法 | 路径 | 描述 | 鉴权 |
|------|------|------|------|
| `POST` | `/api/v1/auth/login` | 获取 JWT 令牌 | — |
| `GET` | `/api/v1/cases` | 案例列表（分页、排序、标签过滤） | — |
| `POST` | `/api/v1/cases` | 创建案例 | ✅ |
| `GET` | `/api/v1/cases/{id}` | 案例详情 | — |
| `GET` | `/api/v1/cases/search?q=` | 全文搜索案例 | — |
| `GET` | `/api/v1/cases/{id}/events` | 获取事件时间线 | — |
| `POST` | `/api/v1/events` | 创建事件节点 | ✅ |
| `GET` | `/api/v1/events/{id}/credibility` | 获取可信度评估 | — |
| `GET` | `/api/v1/feeds` | 数据源列表 | ✅ |
| `POST` | `/api/v1/feeds` | 创建数据源 | ✅ |
| `POST` | `/api/v1/feeds/{id}/collect` | 手动触发采集 | ✅ |
| `GET` | `/api/v1/tags` | 标签列表（含案例计数） | — |

完整文档见 `/docs`（Swagger UI）或 `/redoc`。

---

## 🗄 数据库模型

```
cases          ←→  case_tags  ←→  tags
  │
  ├── event_nodes  ←→  event_node_sources  ←→  sources
  │     └── credibility_assessments
  │
  └── data_feeds
```

8 张表，包含 2 个性能索引（`idx_event_case_time`、`idx_event_time`）。

---

## 🎨 UI 设计规范

### 颜色语义

| 语义 | 颜色 | 用途 |
|------|------|------|
| Brand | `#4f46e5` 靛紫 | 主色调、焦点状态 |
| 高可信 | `#059669` 绿 | 可信度 High |
| 中可信 | `#2563eb` 蓝 | 可信度 Medium |
| 低可信 | `#d97706` 橙 | 可信度 Low |
| 未核实 | `#dc2626` 红 | 可信度 Unverified |

### 组件规范

- 卡片：白色背景 + `border-radius: 10px` + 多层阴影，hover 上浮 2px
- 状态色条：案例卡片左侧 4px 渐变竖条，直观标识案例状态
- 时间线节点：彩色圆点 + 光晕，颜色对应可信度等级
- 可信度圆环：分数圆圈 + 彩色边框，三维进度条渐变填充

---

## 📰 内置媒体源

系统预置 8 个主流中文媒体源，启动即自动采集，无需用户配置：

| 媒体 | 类型 | 采集间隔 |
|------|------|---------|
| 新浪新闻 | HTML Scraper | 30 分钟 |
| 澎湃新闻 | HTML Scraper | 30 分钟 |
| 环球时报 | HTML Scraper | 30 分钟 |
| 央视新闻 | HTML Scraper | 30 分钟 |
| BBC 中文 | RSS | 30 分钟 |
| 联合早报 | HTML Scraper | 30 分钟 |
| 新华网 | HTML Scraper | 30 分钟 |
| 南方都市报 | HTML Scraper | 30 分钟 |

- 内置源在首次启动时自动创建（幂等）
- 管理员可禁用/启用内置源，但不可删除或修改核心字段
- 采集的文章通过 NLP 语义相似度自动归类到对应案例时间线

---

## 🧪 运行测试

```powershell
# 前端单元测试（36个）
cd frontend
npx vitest run

# TypeScript 类型检查
npx vue-tsc --noEmit

# 后端测试
cd backend
$env:PYTHONPATH = $PWD
.venv\Scripts\pytest tests/ -v
```

---

## ⚙️ 环境变量

`backend/.env` 配置项：

```env
DATABASE_URL=sqlite+aiosqlite:///./post_truth.db
JWT_SECRET=<your-secret-key>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme123
CORS_ORIGINS=["http://localhost:5173"]
LOG_LEVEL=INFO
```

生产环境切换 PostgreSQL：
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/post_truth
```

---

## 📋 开发规范

- **提交分支**：`001-case-timeline-verify`（Feature Branch）
- **后端**：遵循 `app/api → app/services → app/models` 分层架构
- **前端**：Composition API + `<script setup>`，所有类型在 `src/types/index.ts` 统一定义
- **测试**：新增组件须在 `tests/components/` 补充测试用例

---

## 📄 许可证

MIT © 2026 后真相时代项目组
