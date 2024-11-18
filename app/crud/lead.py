from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, distinct
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app.models.collector import Collector
from app.models.combined import CollectorLead
from app.schemas.analytics import CollectorAnalytics
from app.models.lead import Lead
from typing import Optional, List
from app.schemas.lead import LeadRead
from app.utils.get_user_vk import get_user_full_name, get_user_info

# Создание записи о переходе лида
async def create_lead_visit(db: AsyncSession, vk_id: str, collector_id: int) -> Optional[CollectorLead]:
    # Получаем или создаем лида
    lead = await get_or_create_lead(db, vk_id)
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
        return None

    # Загружаем CollectorLead с предварительной загрузкой связанных данных
    collector_lead = await db.scalar(
        select(CollectorLead)
        .options(selectinload(CollectorLead.lead))
        .where(
            CollectorLead.collector_id == collector_id,
            CollectorLead.lead_id == lead.id
        )
    )

    if collector_lead and not collector_lead.request_form:
        # Обновляем запись
        collector_lead.request_form = True
        collector_lead.datetime_request = datetime.utcnow()
        await db.commit()
        await db.refresh(collector_lead)
        return collector_lead

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
async def get_or_create_lead(db: AsyncSession, vk_id: str) -> Lead:
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
        full_name=get_user_full_name(vk_id),
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


async def update_lead(db: AsyncSession, phone: str, vk_id: str) -> Lead:
    updated_lead = await db.execute(
        update(Lead)
        .where(Lead.vk_id == vk_id)
        .values(phone=phone)
    )
    
    await db.commit()

    new_lead = await db.scalar(
        select(Lead)
        .where(Lead.vk_id == vk_id)
    )

    return new_lead


async def get_leads_by_collector(
    db: AsyncSession, collector_id: int, search: Optional[str] = None
) -> List[LeadRead]:
    """
    Получить список лидов для указанного коллектора с информацией о фото.

    :param db: Асинхронная сессия базы данных.
    :param collector_id: ID коллектора.
    :param search: Поисковый запрос для фильтрации по имени.
    :return: Список лидов с информацией о фото.
    """
    query = (
        select(Lead)
        .join(Lead.collector_leads)
        .filter(Collector.id == collector_id)
        .options(selectinload(Lead.collector_leads))
        .distinct()
    )
    if search:
        query = query.filter(Lead.full_name.ilike(f"%{search}%"))

    result = await db.execute(query)
    leads = result.scalars().all()

    enriched_leads = []
    for lead in leads:
        try:
            vk_info = await get_user_info(lead.vk_id)
            lead_data = LeadRead.model_validate({
                "id": lead.id,
                "phone": lead.phone,
                "vk_id": lead.vk_id,
                "full_name": lead.full_name,
                "photo": vk_info.get("photo_200"),
            })
            enriched_leads.append(lead_data)
        except RuntimeError:
            # Если информация из ВК не доступна, добавляем без фото
            lead_data = LeadRead.model_validate({
                "id": lead.id,
                "phone": lead.phone,
                "vk_id": lead.vk_id,
                "full_name": lead.full_name,
                "photo": None,
            })
            enriched_leads.append(lead_data)

    return enriched_leads