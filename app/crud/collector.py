from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.models.collector import Collector
from app.schemas.collector import CollectorCreate, CollectorRead
from typing import Optional

# Create a new collector
async def create_collector(db: AsyncSession, user_id: int, collector_data: CollectorCreate) -> CollectorRead:
    collector = Collector(
        name=collector_data.name,
        transcription=collector_data.transcription,
        client_path_type=collector_data.client_path_type.value,  # Конвертируем в строку
        plugin=collector_data.plugin.value if collector_data.plugin else None,  # Конвертируем в строку, если не None
        user_id=user_id,
        description=collector_data.description,
        count_leads=collector_data.count_leads
    )
    db.add(collector)
    await db.commit()
    await db.refresh(collector)
    return CollectorRead.model_validate(collector)

# Read collectors by user ID
async def get_collectors_by_user(db: AsyncSession, user_id: int) -> list[CollectorRead]:
    result = await db.execute(select(Collector).filter(Collector.user_id == user_id))
    collectors = result.scalars().all()
    return [CollectorRead.model_validate(c) for c in collectors]

# Update collector
async def update_collector(db: AsyncSession, collector_id: int, collector_data: CollectorCreate) -> Optional[CollectorRead]:
    result = await db.execute(
        update(Collector)
        .where(Collector.id == collector_id)
        .values(
            name=collector_data.name,
            transcription=collector_data.transcription,
            client_path_type=collector_data.client_path_type.value,  # Конвертируем в строку
            plugin=collector_data.plugin.value if collector_data.plugin else None,  # Конвертируем в строку, если не None
            description=collector_data.description,
            count_leads=collector_data.count_leads
        )
        .returning(Collector)
    )
    collector = result.scalar_one_or_none()
    await db.commit()
    return CollectorRead.model_validate(collector) if collector else None

# Delete collector
async def delete_collector(db: AsyncSession, collector_id: int) -> bool:
    result = await db.execute(delete(Collector).where(Collector.id == collector_id))
    await db.commit()
    return result.rowcount > 0

# Get collector by ID
async def get_collector_by_id(session: AsyncSession, collector_id: int) -> Optional[CollectorRead]:
    result = await session.execute(select(Collector).filter(Collector.id == collector_id))
    result_collector = result.scalar_one_or_none()
    return CollectorRead.model_validate(result_collector) if result_collector else None
