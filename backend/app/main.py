"""FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import create_tables

settings = get_settings()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """App startup: create DB tables and start scheduler."""
    logger.info("Starting up — creating tables…")
    await create_tables()

    # Seed built-in media feeds (idempotent)
    from app.services.builtin_feeds import seed_builtin_feeds
    await seed_builtin_feeds()

    # Start APScheduler
    from app.tasks.scheduler import start_scheduler, stop_scheduler
    start_scheduler()
    logger.info("Scheduler started.")

    yield

    logger.info("Shutting down — stopping scheduler…")
    stop_scheduler()


_DESCRIPTION = """
## 后真相时代 — 案件时间线与信息甄别平台

多来源聚合、NLP 语义去重、可信度量化评估的信息核实系统。

### 主要功能

| 模块 | 端点前缀 | 描述 |
|------|----------|------|
| 身份认证 | `/auth` | JWT 登录令牌 |
| 案例管理 | `/cases` | 创建 / 查询 / 搜索案例 |
| 事件时间轴 | `/cases/{id}/events` | 按时间排列的事件节点 |
| 可信度评估 | `/events/{id}/credibility` | 三维评分 + 来源对比 |
| 数据源管理 | `/feeds` | RSS/Atom/Scraper 采集配置 |
| 标签 | `/tags` | 案例分类标签 |

### 认证方式

受保护的写操作需要在 `Authorization` 头中携带 `Bearer <JWT>` 令牌。
通过 `POST /api/v1/auth/login` 获取令牌。
"""

app = FastAPI(
    title="后真相时代 API",
    description=_DESCRIPTION,
    version="0.2.0",
    contact={
        "name": "项目维护者",
        "url": "https://github.com/post-truth-era/case-timeline-verify",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "auth",        "description": "JWT 登录与注销"},
        {"name": "cases",       "description": "案例 CRUD、热度排序、全文搜索"},
        {"name": "events",      "description": "事件时间轴，支持时间范围过滤"},
        {"name": "credibility", "description": "三维可信度评分与来源对比"},
        {"name": "feeds",       "description": "数据源配置与采集触发"},
        {"name": "tags",        "description": "案例标签管理"},
        {"name": "system",      "description": "健康检查"},
    ],
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500},
    )


# Mount routers
from app.api.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
