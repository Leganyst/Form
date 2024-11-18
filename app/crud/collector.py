from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.orm import selectinload
from app.models.collector import Collector
from app.models.combined import CollectorLead  
from app.schemas.collector import CollectorCreate, CollectorRead, CollectorReadWithVkId
from app.schemas.analytics import CollectorAnalytics
from app.models.collector import Collector
from app.models.lead import Lead
from app.models.group import Group
from typing import Optional, List
from sqlalchemy import func

# Создание нового коллектора
async def create_collector(db: AsyncSession, group_id: int, collector_data: CollectorCreate) -> CollectorRead:
    collector = Collector(
        name=collector_data.name,
        transcription=collector_data.transcription,
        client_path_type=collector_data.client_path_type.value.upper(),
        plugin=collector_data.plugin.value.upper() if collector_data.plugin else None,
        group_id=group_id,
        description=collector_data.description,
        count_leads=collector_data.count_leads
    )
    db.add(collector)
    group = await db.execute(select(Group).where(Group.id == group_id))
    group = group.scalar_one_or_none()
    group.collector_count += 1
    
    await db.commit()
    await db.refresh(collector)


    collector_dict = {
        "id": collector.id,
        "name": collector.name,
        "description": collector.description,
        "transcription": collector.transcription,
        "client_path_type": collector.client_path_type,
        "client_path": collector.client_path,
        "plugin": collector.plugin,
        "count_leads": collector.count_leads,
        "first_bonus": collector.first_bonus,
        "second_bonus": collector.second_bonus,
        "third_bonus": collector.third_bonus
    }
    return CollectorRead(**collector_dict)


# Получение всех коллекторов по ID пользователя
async def get_collectors_by_group(db: AsyncSession, group_id: int) -> List[CollectorRead]:
    result = await db.execute(
        select(Collector)
        .options(selectinload(Collector.group), selectinload(Collector.collector_leads))
        .filter(Collector.group_id == group_id)
    )
    collectors = result.scalars().all()

    return [
        CollectorRead(**{
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "transcription": c.transcription,
            "client_path_type": c.client_path_type,
            "client_path": c.client_path,
            "plugin": c.plugin,
            "count_leads": c.count_leads,
            "first_bonus": c.first_bonus,
            "second_bonus": c.second_bonus,
            "third_bonus": c.third_bonus
        }) for c in collectors
    ]


# Обновление коллектора по его ID
async def update_collector(
    db: AsyncSession, collector_id: int, collector_data: CollectorCreate
) -> Optional[CollectorRead]:
    result = await db.execute(
        update(Collector)
        .where(Collector.id == collector_id)
        .values(
            name=collector_data.name,
            transcription=collector_data.transcription,
            client_path_type=collector_data.client_path_type.value.upper(),
            client_path=collector_data.client_path,
            plugin=collector_data.plugin.value.upper() if collector_data.plugin else None,
            description=collector_data.description,
            count_leads=collector_data.count_leads,
            request_phone_numbers=collector_data.request_phone_numbers,
            first_bonus=collector_data.first_bonus,
            second_bonus=collector_data.second_bonus,
            third_bonus=collector_data.third_bonus
        )
        .returning(Collector)
    )
    await db.commit()
    collector: Collector = result.scalar_one_or_none()

    if collector:
        # Явно обновляем объект, чтобы загрузить все его атрибуты
        await db.refresh(collector)
        collector_dict = {
            "id": collector.id,
            "name": collector.name,
            "description": collector.description,
            "transcription": collector.transcription,
            "client_path_type": collector.client_path_type,
            "client_path": collector.client_path,
            "plugin": collector.plugin,
            "count_leads": collector.count_leads,
            "request_phone_numbers": collector.request_phone_numbers,
            "first_bonus": collector.first_bonus,
            "second_bonus": collector.second_bonus,
            "third_bonus": collector.third_bonus
        }
        return CollectorRead(**collector_dict)
    return None


# Удаление коллектора по его ID
async def delete_collector(db: AsyncSession, collector_id: int) -> bool:
    result = await db.execute(delete(Collector).where(Collector.id == collector_id))
    
    group = await db.execute(select(Group).where(Group.id == collector_id))
    group = group.scalar_one_or_none()
    group.collector_count -= 1
    await db.commit()
    return result.rowcount > 0


# Получение коллектора по его ID
async def get_collector_by_id(session: AsyncSession, collector_id: int) -> Optional[CollectorReadWithVkId]:
    result = await session.execute(
        select(Collector)
        .options(selectinload(Collector.group), selectinload(Collector.collector_leads))
        .filter(Collector.id == collector_id)
    )
    result_collector = result.scalar_one_or_none()
    
    if not result_collector:
        return None
    
    group_vk_id = await session.execute(
        select(Group.vk_id)
        .where(Group.id == result_collector.group_id)
    )
    group_vk_id = group_vk_id.scalar_one_or_none()

    if result_collector:
        collector_dict = {
            "id": result_collector.id,
            "name": result_collector.name,
            "description": result_collector.description,
            "transcription": result_collector.transcription,
            "client_path_type": result_collector.client_path_type,
            "client_path": result_collector.client_path,
            "plugin": result_collector.plugin,
            "count_leads": result_collector.count_leads,
            "first_bonus": result_collector.first_bonus,
            "second_bonus": result_collector.second_bonus,
            "third_bonus": result_collector.third_bonus,
            "vk_id": group_vk_id
        }
        return CollectorReadWithVkId(**collector_dict)
    return None


# Получение аналитики по коллекторам
async def get_collector_analytics(db: AsyncSession, collector_id: int) -> Optional[CollectorAnalytics]:
    # Проверяем, существует ли коллектор
    collector = await db.execute(select(Collector).where(Collector.id == collector_id))
    collector = collector.scalar_one_or_none()
    if not collector:
        return None

    # Подсчитываем количество лидов, которые отправили заявку (request_form=True)
    lead_count_query = await db.execute(
        select(func.count(CollectorLead.lead_id))
        .where(CollectorLead.collector_id == collector_id)
        .where(CollectorLead.request_form == True)
    )
    lead_count = lead_count_query.scalar() or 0

    # Подсчитываем общее количество посещений (лиды, у которых request_form=False)
    visit_count_query = await db.execute(
        select(func.count(CollectorLead.lead_id))
        .where(CollectorLead.collector_id == collector_id)
    )
    visit_count = visit_count_query.scalar() or 0

    # Расчёт CR (лиды / посещения * 100%)
    conversion_rate = (lead_count / visit_count * 100) if visit_count > 0 else 0

    # Возвращаем объект CollectorAnalytics для валидации
    return CollectorAnalytics(
        collector_id=collector_id,
        leads_count=lead_count,
        visit_count=visit_count,
        conversion_rate=conversion_rate
    )