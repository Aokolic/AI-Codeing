# ⚡ 后真相时代 — 信息甄别平台

> 多来源聚合 · 事件时间线追踪 · 三维可信度量化评估 · 智能事件归类

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Backend Tests](https://img.shields.io/badge/Backend_Tests-81%20passed-059669)](./backend/tests)
[![Frontend Tests](https://img.shields.io/badge/Frontend_Tests-36%20passed-059669)](./frontend/tests)

---

## 📖 项目简介

**后真相时代**是一套面向新闻核实与信息甄别场景的全栈 Web 平台。系统围绕"舆论案例"构建，将同一事件的多方报道聚合为统一时间线，并通过权威性、时效性、交叉验证三个维度对每个事件节点打出可信度评分，帮助读者快速判断信息真实性。

### 核心功能

| 功能模块 | 描述 |
|---------|------|
| 🗂 案例管理 | 创建、检索、搜索热度排序的信息案例 |
| 📅 事件时间线 | 按时间轴展示案例内所有事件节点，可信度颜色编码 |
| 🔍 三维可信度评估 | 权威性 · 时效性 · 交叉验证，综合评分 0-100 |
| 📡 数据源管理 | RSS/JSON 采集源配置，支持 Cron 定时触发与单源手动采集 |
| 📰 内置媒体采集 | 8 个国际中文媒体 RSS 源零配置自动采集，每 30 分钟更新 |
| 🧠 智能事件归类 | jieba 实体提取 + sentence-transformers 语义匹配，双层自动归类 |
| 🏷 标签分类 | 多维标签体系，案例交叉归类 |

---

## 🏗 技术栈

### 后端
- **FastAPI** 0.135 — 异步 REST API，自动生成 OpenAPI 文档
- **SQLAlchemy** 2.0 (async) + **aiosqlite** — 异步 ORM，生产可切换 PostgreSQL
- **Alembic** — 数据库版本迁移
- **Pydantic v2** + **pydantic-settings** — 数据校验与配置管理
- **APScheduler** — 数据源定时采集任务
- **jieba** — 中文分词与实体提取（人名/地名/机构名）
- **sentence-transformers** — 语义向量编码，余弦相似度事件归类
- **feedparser** + **BeautifulSoup4** — RSS/HTML 内容解析
- **pytest** + **pytest-asyncio** — 81 个后端测试用例

### 前端
- **Vue 3.4** (Composition API + `<script setup>`)
- **TypeScript 5.3** (strict 模式，vue-tsc 零错误)
- **Vite 5** — 构建工具，内置 `/api` → 后端代理
- **Naive UI 2.38** — 组件库
- **Vue Router 4** — SPA 路由
- **Axios** — HTTP 客户端
- **Vitest** + **@vue/test-utils** — 7 个测试文件，36 个测试用例全部通过

---

## 📂 目录结构

```
AI-Codeing/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # 路由层 (cases/events/credibility/feeds/tags)
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── schemas/            # Pydantic 请求响应模式
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── collector.py    # RSS 采集 + 双层 NLP 事件归类
│   │   │   ├── entity_extractor.py  # jieba 实体提取 + Jaccard 重叠
│   │   │   ├── nlp_matcher.py  # sentence-transformers 语义匹配
│   │   │   ├── credibility.py  # 三维可信度评估引擎
│   │   │   ├── builtin_feeds.py # 8 个内置 RSS 源定义
│   │   │   └── ...
│   │   ├── tasks/              # APScheduler 定时任务
│   │   ├── config.py           # pydantic-settings 配置
│   │   ├── database.py         # 异步数据库引擎
│   │   └── main.py             # FastAPI 应用入口
│   ├── alembic/                # 数据库迁移脚本
│   ├── tests/                  # 后端测试套件 (81 个用例)
│   │   ├── unit/               # 单元测试
│   │   └── contract/           # API 契约测试
│   └── requirements.txt
│
└── frontend/                   # Vue 3 前端
    ├── src/
    │   ├── api/                # HTTP 模块 (cases/events/credibility/feeds)
    │   ├── components/         # 通用组件
    │   │   ├── AppLayout.vue   # 全局导航布局
    │   │   ├── CaseCard.vue    # 案例卡片
    │   │   ├── CredibilityBadge.vue  # 可信度徽章
    │   │   ├── CredibilityPanel.vue  # 可信度详情面板
    │   │   ├── EventCard.vue   # 事件卡片（含来源图标 + 可信度颜色编码）
    │   │   ├── FeedStatusPanel.vue   # 数据源状态面板（单源采集）
    │   │   ├── SearchBar.vue   # 搜索栏
    │   │   └── Timeline.vue    # 事件时间线
    │   ├── composables/
    │   │   └── useTimeline.ts  # 时间线状态管理 composable
    │   ├── pages/
    │   │   ├── HomePage.vue        # 首页（标签过滤 + 热度排行）
    │   │   ├── CaseDetailPage.vue  # 案例详情页 + 时间线 + 可信度抽屉
    │   │   ├── SearchResultPage.vue # 搜索结果页
    │   │   └── AdminPage.vue       # 数据源管理面板
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

# 安装 NLP 依赖（jieba + sentence-transformers）
pip install jieba sentence-transformers

# 初始化数据库
$env:PYTHONPATH = $PWD
.venv\Scripts\alembic upgrade head

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

## 🌐 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| `GET` | `/api/v1/cases` | 案例列表（分页、排序、标签过滤） |
| `POST` | `/api/v1/cases` | 创建案例 |
| `GET` | `/api/v1/cases/{id}` | 案例详情 |
| `GET` | `/api/v1/cases/search?q=` | 全文搜索案例 |
| `GET` | `/api/v1/cases/{id}/events` | 获取事件时间线 |
| `POST` | `/api/v1/events` | 创建事件节点 |
| `GET` | `/api/v1/events/{id}/credibility` | 获取可信度评估 |
| `GET` | `/api/v1/feeds` | 数据源列表 |
| `POST` | `/api/v1/feeds` | 创建数据源 |
| `POST` | `/api/v1/feeds/{id}/collect` | 手动触发单源采集（同步等待完成） |
| `GET` | `/api/v1/tags` | 标签列表（含案例计数） |

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
| Brand | `#ef4444` 红 | 主色调、强调元素 |
| 高可信 | `#059669` 绿 | 可信度 High |
| 中可信 | `#7c3aed` 紫 | 可信度 Medium |
| 低可信 | `#d97706` 橙 | 可信度 Low |
| 未核实 | `#dc2626` 红 | 可信度 Unverified |

### 组件规范

- 卡片：白色背景 + `border-radius: 10px` + 多层阴影，hover 上浮 2px
- 状态色条：案例卡片左侧 4px 渐变竖条，直观标识案例状态
- 时间线节点：彩色圆点 + 光晕，颜色对应可信度等级
- 日期标签：彩色背景 + 白色文字，直观区分可信度
- 可信度圆环：分数圆圈 + 彩色边框，三维进度条渐变填充

---

## 📰 内置媒体源

系统预置 8 个国际中文媒体 RSS 源，启动即自动采集，无需用户配置：

| 媒体 | 类型 | 采集间隔 |
|------|------|---------|
| BBC 中文 | RSS | 30 分钟 |
| 德国之声中文 | RSS | 30 分钟 |
| 法广 RFI 中文 | RSS | 30 分钟 |
| 纽约时报中文 | RSS | 30 分钟 |
| 韩联社中文 | RSS | 30 分钟 |
| NHK 中文 | JSON | 30 分钟 |
| 联合早报 | RSS | 30 分钟 |
| CNA 中央通讯社 | RSS | 30 分钟 |

- 内置源在首次启动时自动创建（幂等）
- 管理员可禁用/启用内置源，但不可删除
- 采集的文章通过双层 NLP 自动归类：先 jieba 实体重叠匹配，再 sentence-transformers 语义相似度验证

---

## 🧪 运行测试

```powershell
# 前端单元测试（36 个）
cd frontend
npx vitest run

# TypeScript 类型检查
npx vue-tsc --noEmit

# 后端测试（81 个）
cd backend
$env:PYTHONPATH = $PWD
.venv\Scripts\pytest tests/ -v
```

---

## ⚙️ 环境变量

`backend/.env` 配置项：

```env
DATABASE_URL=sqlite+aiosqlite:///./post_truth.db
CORS_ORIGINS=["http://localhost:5173"]
LOG_LEVEL=INFO
CASE_SIMILARITY_THRESHOLD=0.45
CASE_ENTITY_OVERLAP_THRESHOLD=0.3
```

生产环境切换 PostgreSQL：
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/post_truth
```

---

## 📋 开发规范

- **后端**：遵循 `app/api → app/services → app/models` 分层架构
- **前端**：Composition API + `<script setup>`，所有类型在 `src/types/index.ts` 统一定义
- **测试**：新增组件须在 `tests/components/` 补充测试用例
- **NLP 配置**：通过 `CASE_SIMILARITY_THRESHOLD` 和 `CASE_ENTITY_OVERLAP_THRESHOLD` 调节事件归类灵敏度

---

## 📄 许可证

MIT © 2026 后真相时代项目组
