from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
import pytz
from app.integrations.telegram import send_telegram_message
from app.crud.collector import get_collector_by_id
from app.crud.group import get_group_by_id
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.routers.dependencies.auth import get_group_depend
from app.schemas.group import GroupRead
from app.core.config import settings
from typing import List

from app.utils.get_user_vk import get_user_info

router = APIRouter()

@router.post("/collectors/{collector_id}/complaint", status_code=201, tags=["collector"])
async def file_complaint(
    collector_id: int,
    complaint_text: str,
    vk_user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Подать жалобу на сборщик. Жалоба отправляется админам в Telegram.
    """
    # Получаем информацию о сборщике
    collector = await get_collector_by_id(db, collector_id)
    if not collector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collector not found")
    
    user_info = await get_user_info(vk_user_id)
    
    # Устанавливаем часовой пояс для Москвы
    moscow_tz = pytz.timezone('Europe/Moscow')
    # Получаем текущее время в UTC
    utc_now = datetime.now(pytz.utc)
    # Преобразуем текущее время в часовой пояс Москвы
    moscow_now = utc_now.astimezone(moscow_tz)
    # Форматируем дату и время
    formatted_time = moscow_now.strftime("%Y-%m-%d %H:%M:%S")

    # Формируем текст жалобы
    message = (
        f"🚨 *Жалоба на сборщик*\n"
        f"——————————————\n"
        f"👤 *Пользователь:*\n"
        f"• *VK ID:* `{user_info.get('vk_id') or 'N/A'}`\n"
        f"• *Имя:* `{user_info.get('full_name') or 'N/A'}`\n\n"
        f"📋 *Сборщик:*\n"
        f"• *Название:* `{collector.name}`\n"
        f"• *ID:* `{collector.id}`\n"
        f"• *Описание:* `{collector.description or 'Нет описания'}`\n\n"
        f"📝 *Текст жалобы:*\n"
        f"```\n{complaint_text}\n```\n"
        f"——————————————\n"
        f"📅 *Дата подачи:* {formatted_time or 'N/A'}"
    )

    # Отправляем жалобу в Telegram
    admin_ids = [settings.admin_id_first, settings.admin_id_second, settings.admin_id_third]
    await send_telegram_message(message, admin_ids)

    return {"detail": "Complaint successfully submitted"}