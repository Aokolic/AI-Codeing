"""Seed script — populate DB with 10+ realistic Chinese news cases (SC-001)."""
from __future__ import annotations

import asyncio
import sys
import uuid

# Ensure UTF-8 output on Windows GBK consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import Base
from app.models.case import Case, CaseStatus, CaseTag, Tag
from app.models.event_node import EventNode
from app.models.source import EventNodeSource, Source, SourceType

settings = get_settings()

SEED_DATA: list[dict[str, Any]] = [
    {
        "title": "新冠病毒溯源争议",
        "description": "关于新冠病毒起源的多方不同声明与科学调查进展",
        "tags": ["公共卫生", "科学"],
        "events": [
            {"title": "WHO发布溯源调查报告", "days_ago": 500, "sources": [("世界卫生组织", SourceType.government)]},
            {"title": "多国科学家联名质疑报告结论", "days_ago": 480, "sources": [("《自然》杂志", SourceType.academic)]},
            {"title": "美国情报机构发布独立评估", "days_ago": 400, "sources": [("路透社", SourceType.mainstream_media), ("CNN", SourceType.mainstream_media)]},
        ],
    },
    {
        "title": "某省高考成绩造假事件",
        "description": "网传某省份高考录取通知书批量伪造，多名学生被冒名顶替入学",
        "tags": ["教育", "腐败"],
        "events": [
            {"title": "当事人发文：我的大学被人偷走了", "days_ago": 200, "sources": [("微博@当事人", SourceType.social_media)]},
            {"title": "教育部回应展开调查", "days_ago": 192, "sources": [("教育部官网", SourceType.government)]},
            {"title": "涉事人员被移送司法机关", "days_ago": 150, "sources": [("新华社", SourceType.mainstream_media), ("人民日报", SourceType.mainstream_media)]},
        ],
    },
    {
        "title": "某知名医院虚假手术事件",
        "description": "患者自述在三甲医院接受了不必要的高价手术，疑似医疗欺诈",
        "tags": ["医疗", "消费者权益"],
        "events": [
            {"title": "患者在社交媒体发布维权视频", "days_ago": 90, "sources": [("抖音用户", SourceType.social_media)]},
            {"title": "国家卫健委介入调查通报", "days_ago": 82, "sources": [("国家卫健委", SourceType.government)]},
            {"title": "医院院长被停职", "days_ago": 60, "sources": [("央视新闻", SourceType.mainstream_media)]},
        ],
    },
    {
        "title": "芯片制造商数据造假传闻",
        "description": "某国内芯片企业被指控虚报研发成果与芯片良率，投资者损失惨重",
        "tags": ["科技", "金融"],
        "events": [
            {"title": "做空机构发布研究报告质疑财务数据", "days_ago": 300, "sources": [("浑水研究", SourceType.academic)]},
            {"title": "公司发声明否认指控", "days_ago": 298, "sources": [("公司官网", SourceType.government)]},
            {"title": "证监会立案调查", "days_ago": 280, "sources": [("证监会", SourceType.government), ("财新", SourceType.mainstream_media)]},
            {"title": "核心高管辞职", "days_ago": 240, "sources": [("21世纪经济报道", SourceType.mainstream_media)]},
        ],
    },
    {
        "title": "网红食品虚假宣传案",
        "description": "某网红品牌声称产品功效未经科学验证，被消协点名批评",
        "tags": ["食品安全", "消费者权益"],
        "events": [
            {"title": "消费者投诉产品无效果", "days_ago": 120, "sources": [("微博话题", SourceType.social_media)]},
            {"title": "消费者协会专项报告发布", "days_ago": 100, "sources": [("中国消费者协会", SourceType.government)]},
            {"title": "品牌下架问题产品并致歉", "days_ago": 85, "sources": [("品牌官微", SourceType.social_media)]},
        ],
    },
    {
        "title": "洪水灾情应对争议",
        "description": "某地区洪涝灾害期间，官方伤亡数字与民间统计差异悬殊",
        "tags": ["灾害", "政府透明度"],
        "events": [
            {"title": "暴雨引发严重洪灾，大量地铁隧道被淹", "days_ago": 600, "sources": [("省气象局", SourceType.government)]},
            {"title": "官方公布伤亡人数", "days_ago": 596, "sources": [("省政府官网", SourceType.government)]},
            {"title": "民间志愿者统计数字引发广泛讨论", "days_ago": 590, "sources": [("微信公众号", SourceType.social_media), ("财新传媒", SourceType.mainstream_media)]},
            {"title": "第三方独立调查报告发布", "days_ago": 540, "sources": [("中国政法大学", SourceType.academic)]},
        ],
    },
    {
        "title": "明星学历造假疑云",
        "description": "知名流量明星被指控所谓名校学历系伪造，学校官方未能核实",
        "tags": ["娱乐", "学术诚信"],
        "events": [
            {"title": "网友发帖质疑明星名校学历真实性", "days_ago": 400, "sources": [("知乎用户", SourceType.social_media)]},
            {"title": "涉事大学发公告称无此毕业生", "days_ago": 395, "sources": [("大学官网", SourceType.academic)]},
            {"title": "明星工作室发声明自称误解", "days_ago": 392, "sources": [("明星官方微博", SourceType.social_media)]},
        ],
    },
    {
        "title": "自动驾驶事故责任认定纠纷",
        "description": "某品牌电动车辅助驾驶功能引发交通事故，厂家与车主陷入法律争议",
        "tags": ["科技", "法律", "交通安全"],
        "events": [
            {"title": "车主发布事故行车记录仪视频", "days_ago": 50, "sources": [("抖音", SourceType.social_media)]},
            {"title": "厂商声明系驾驶员操作失误", "days_ago": 48, "sources": [("厂商官网", SourceType.government)]},
            {"title": "交警部门发布事故鉴定报告", "days_ago": 30, "sources": [("市公安局交管局", SourceType.government), ("中央电视台", SourceType.mainstream_media)]},
        ],
    },
    {
        "title": "境外势力操控网络舆论调查",
        "description": "某平台被指有组织地散布政治虚假信息，平台方拒绝配合核查",
        "tags": ["网络安全", "政治"],
        "events": [
            {"title": "研究机构发布虚假信息传播网络图谱", "days_ago": 180, "sources": [("斯坦福互联网观察站", SourceType.academic)]},
            {"title": "平台方发表回应否认指控", "days_ago": 175, "sources": [("平台官方博客", SourceType.social_media)]},
            {"title": "国会听证会要求平台提交数据", "days_ago": 140, "sources": [("路透社", SourceType.mainstream_media), ("BBC", SourceType.mainstream_media)]},
        ],
    },
    {
        "title": "国产疫苗保护效力争议",
        "description": "某国产新冠疫苗真实世界保护率数据引发学术界与厂商之间的技术争论",
        "tags": ["公共卫生", "科学"],
        "events": [
            {"title": "权威期刊发表研究称保护率低于预期", "days_ago": 350, "sources": [("《柳叶刀》", SourceType.academic)]},
            {"title": "疫苗厂商发表声明质疑研究方法", "days_ago": 345, "sources": [("厂商官网", SourceType.government)]},
            {"title": "国家疾控中心发布大规模真实世界数据", "days_ago": 310, "sources": [("国家疾控中心", SourceType.government), ("新华社", SourceType.mainstream_media)]},
        ],
    },
]


async def seed(db: AsyncSession) -> None:
    print("开始填充种子数据…")
    tag_cache: dict[str, str] = {}

    for case_data in SEED_DATA:
        case_id = str(uuid.uuid4())
        case = Case(
            id=case_id,
            title=case_data["title"],
            description=case_data["description"],
            status=CaseStatus.active,
            created_at=datetime.now(timezone.utc) - timedelta(days=max(e["days_ago"] for e in case_data["events"]) + 1),
            hotness_score=0.0,
        )
        db.add(case)

        for tag_name in case_data["tags"]:
            if tag_name not in tag_cache:
                tag = Tag(id=str(uuid.uuid4()), name=tag_name)
                db.add(tag)
                await db.flush()
                tag_cache[tag_name] = tag.id
            db.add(CaseTag(case_id=case_id, tag_id=tag_cache[tag_name]))

        for event_data in case_data["events"]:
            event_id = str(uuid.uuid4())
            event_time = datetime.now(timezone.utc) - timedelta(days=event_data["days_ago"])
            event = EventNode(
                id=event_id,
                case_id=case_id,
                title=event_data["title"],
                summary=f"{event_data['title']} — 详细报道摘要（种子数据）",
                event_time=event_time,
            )
            db.add(event)
            await db.flush()

            for src_name, src_type in event_data["sources"]:
                src_id = str(uuid.uuid4())
                src = Source(
                    id=src_id,
                    name=src_name,
                    source_type=src_type,
                    url=f"https://example.com/{uuid.uuid4().hex[:8]}",
                    reputation_score=75.0,
                    collected_at=event_time,
                )
                db.add(src)
                await db.flush()
                db.add(EventNodeSource(event_node_id=event_id, source_id=src_id))

    await db.commit()
    print(f"[OK] Seeded {len(SEED_DATA)} cases with events and sources.")


async def main() -> None:
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        await seed(db)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
