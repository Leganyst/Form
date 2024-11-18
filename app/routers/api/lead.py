from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.crud.lead import (
    create_lead_visit,
    get_leads_by_collector,
    submit_lead_request,
    get_collector_analytics,
    update_lead
)
from app.routers.dependencies.auth import get_group_depend
from app.schemas.analytics import CollectorAnalytics
from app.schemas.combined import CollectorLeadRead
from app.schemas.lead import LeadCreate, LeadRead
from app.models.combined import CollectorLead
from app.models.lead import Lead
from typing import Optional, List

from app.schemas.group import GroupRead

router = APIRouter()

# Эндпоинт для создания записи о переходе лида с использованием vk_id
@router.post("/collectors/{collector_id}/leads", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
async def create_lead(
    collector_id: int,
    lead_data: LeadCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создает новую запись о переходе лида с использованием vk_id для указанного collector_id, если такой записи еще нет.
    Устанавливает флаг `checked_form=True` для нового лида.
    """
    lead = await create_lead_visit(db, lead_data.vk_id, collector_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Lead visit already recorded for this collector.")
    return LeadRead.model_validate(lead)

# Эндпоинт для обновления информации о лидах при отправке заявки
@router.patch("/collectors/{collector_id}/leads/{vk_id}", response_model=CollectorLeadRead)
async def update_lead_request(
    collector_id: int,
    vk_id: str,
    phone_number: str = None,
    db: AsyncSession = Depends(get_db)
):
    lead = await submit_lead_request(db, vk_id, collector_id)
    await update_lead(db, phone_number, vk_id)

    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found or request already submitted.")

    # Обновляем объект и возвращаем его
    await db.refresh(lead)
    return CollectorLeadRead.model_validate(lead)


# Эндпоинт для получения аналитики по коллектору
@router.get("/collectors/{collector_id}/analytics", response_model=CollectorAnalytics)
async def get_collector_analytics_endpoint(
    collector_id: int,
    period: str,
    db: AsyncSession = Depends(get_db),
    user: GroupRead = Depends(get_group_depend)
):
    """
    Получает аналитику для указанного collector_id за период.
    Период может быть "day", "week" или "month".
    """
    
    try:
        analytics = await get_collector_analytics(db, collector_id, period)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid period. Choose 'day', 'week', or 'month'.")
    return analytics


@router.get("/collectors/{collector_id}/leads", response_model=List[LeadRead], tags=["leads"])
async def get_leads_endpoint(
    collector_id: int,
    search: Optional[str] = Query(None, description="Поиск по имени лидов"),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить список лидов для указанного коллектора. 
    Можно использовать поисковый параметр `search` для фильтрации по имени.
    
    - **collector_id**: ID коллектора.
    - **search**: Поисковый параметр для фильтрации по имени.
    """
    leads = await get_leads_by_collector(db, collector_id, search)
    if not leads:
        raise HTTPException(status_code=404, detail="No leads found for this collector.")
    return leads