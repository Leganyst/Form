from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app.models.collector import Collector
from app.models.combined import CollectorLead
from app.schemas.analytics import CollectorAnalytics
from typing import Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.combined import CollectorLead
from app.models.lead import Lead
from typing import Optional

# Создание записи о переходе лида
async def create_lead_visit(db: AsyncSession, vk_id: str, collector_id: int, full_name: str) -> Optional[CollectorLead]:
    # Получаем или создаем лида
    lead = await get_or_create_lead(db, vk_id, full_name)
    if not lead:
        # Если создание лида не удалось, возвращаем None
        return None

    # Проверяем, существует ли запись в CollectorLead для данного collector_id и lead_id
    existing_lead = await db.scalar(
        select(CollectorLead).where(
            CollectorLead.collector_id == collector_id,
            CollectorLead.lead_id == lead.id
        )
    )
    
    if existing_lead:
        # Если запись уже существует, просто возвращаем её, ничего не изменяя
        lead_result = await db.scalar(
            select(Lead).where(Lead.id == lead.id)
        )
        return lead_result

    # Создаем новую запись в CollectorLead с checked_form=True
    new_lead = CollectorLead(
        collector_id=collector_id,
        lead_id=lead.id,
        checked_form=True,
        request_form=False,
        datetime_request=None
    )
    db.add(new_lead)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return None
    await db.refresh(new_lead)
    
    lead_result = await db.scalar(
        select(Lead).where(Lead.id == new_lead.lead_id)
    )
    
    return lead_result

# Обновление записи лида при отправке заявки
async def submit_lead_request(db: AsyncSession, vk_id: str, collector_id: int) -> Optional[CollectorLead]:
    # Сначала ищем лида по vk_id
    lead = await db.scalar(
        select(Lead).where(Lead.vk_id == vk_id)
    )
    
    if not lead:
        # Если лида с таким vk_id нет, ничего не делаем и возвращаем None
        return None

    # Теперь ищем запись в CollectorLead для данного lead_id и collector_id
    collector_lead = await db.scalar(
        select(CollectorLead).where(
            CollectorLead.collector_id == collector_id,
            CollectorLead.lead_id == lead.id
        )
    )

    # Проверяем, что запись существует и что заявка еще не отправлена
    if collector_lead and not collector_lead.request_form:
        # Обновляем запись, устанавливая request_form=True и добавляя время заявки
        await db.execute(
            update(CollectorLead)
            .where(CollectorLead.collector_id == collector_id, CollectorLead.lead_id == lead.id)
            .values(request_form=True, datetime_request=datetime.utcnow())
        )
        await db.commit()
        await db.refresh(collector_lead)
        
        return collector_lead
        
    # Если запись не существует или заявка уже отправлена, возвращаем None
    return None


# Получение аналитики для коллектора
async def get_collector_analytics(db: AsyncSession, collector_id: int, period: str) -> CollectorAnalytics:
    # Определение временного диапазона для анализа
    start_date = datetime.utcnow() - {
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30)
    }.get(period, timedelta(days=1))

    # Подсчет количества лидов и просмотров
    leads_count = await db.scalar(
        select(func.count(CollectorLead.lead_id))
        .where(
            CollectorLead.collector_id == collector_id,
            CollectorLead.request_form == True,
            CollectorLead.datetime_request >= start_date
        )
    )

    visit_count = await db.scalar(
        select(func.count(CollectorLead.lead_id))
        .where(
            CollectorLead.collector_id == collector_id,
            CollectorLead.checked_form == True,
            CollectorLead.datetime_request >= start_date
        )
    )

    # Расчет коэффициента конверсии (CR)
    conversion_rate = (leads_count / visit_count * 100) if visit_count else 0.0

    return CollectorAnalytics(
        collector_id=collector_id,
        leads_count=leads_count,
        visit_count=visit_count,
        conversion_rate=conversion_rate
    )


# Проверка на существование лида и создание нового, если его нет
async def get_or_create_lead(db: AsyncSession, vk_id: str, full_name: str) -> Lead:
    # Ищем лида с заданным vk_id
    existing_lead = await db.scalar(
        select(Lead).where(Lead.vk_id == vk_id)
    )

    if existing_lead:
        # Если такой лид уже существует, возвращаем его
        return existing_lead

    # Если лида с таким vk_id нет, создаем новый объект Lead
    new_lead = Lead(
        vk_id=vk_id,
        full_name=full_name,
        phone=None  # Поле phone пока оставляем пустым
    )
    db.add(new_lead)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return None
    await db.refresh(new_lead)
    return new_lead