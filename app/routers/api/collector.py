from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.notification import (
    create_notification,
    get_notifications_for_user,
    update_notification_status
)
from app.schemas.notification import NotificationCreate, NotificationRead, UserNotificationStatusRead
from app.routers.dependencies.auth import get_user_depend

router = APIRouter()


# Создание уведомления
@router.post(
    "/notifications",
    response_model=NotificationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать уведомление",
    tags=["notification"],
    description="Создает новое уведомление в системе. Обычно используется администратором или системной службой.",
    responses={
        201: {
            "description": "Уведомление успешно создано",
            "content": {
                "application/json": {
                    "example": NotificationRead.example()
                }
            }
        },
        401: {
            "description": "Неавторизованная попытка создания уведомления",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        },
        403: {
            "description": "Доступ запрещён",
            "content": {
                "application/json": {
                    "example": {"detail": "Forbidden"}
                }
            }
        }
    }
)
async def create_notification_endpoint(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создает новое уведомление в системе.

    - **notification_data**: Данные для создания уведомления, такие как заголовок, описание и тип уведомления.
    """
    return await create_notification(db, notification_data)


# Получение уведомлений для текущего пользователя
@router.get(
    "/notifications",
    response_model=list[NotificationRead],
    summary="Получить уведомления пользователя",
    tags=["notification"],
    description="Возвращает список уведомлений для текущего авторизованного пользователя.",
    responses={
        200: {
            "description": "Список уведомлений пользователя",
            "content": {
                "application/json": {
                    "example": [NotificationRead.example()]
                }
            }
        },
        401: {
            "description": "Неавторизованная попытка получения уведомлений",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        }
    }
)
async def get_notifications_for_user_endpoint(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_user_depend)
):
    """
    Возвращает список уведомлений, связанных с текущим пользователем.

    - **user**: Текущий авторизованный пользователь.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return await get_notifications_for_user(db, user["id"])


# Обновление статуса уведомления
@router.patch(
    "/notifications/{notification_id}",
    response_model=UserNotificationStatusRead,
    summary="Обновить статус уведомления",
    tags=["notification"],
    description="Обновляет статус уведомления для текущего пользователя, позволяя отметить уведомление как прочитанное или скрытое.",
    responses={
        200: {
            "description": "Статус уведомления успешно обновлён",
            "content": {
                "application/json": {
                    "example": UserNotificationStatusRead.example()
                }
            }
        },
        401: {
            "description": "Неавторизованная попытка обновления статуса уведомления",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        },
        404: {
            "description": "Уведомление не найдено",
            "content": {
                "application/json": {
                    "example": {"detail": "Notification not found"}
                }
            }
        }
    }
)
async def update_notification_status_endpoint(
    notification_id: int,
    is_read: bool = None,
    is_hidden: bool = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_user_depend)
):
    """
    Обновляет статус уведомления для текущего пользователя.

    - **notification_id**: ID уведомления, которое требуется обновить.
    - **is_read**: Если передано `True`, уведомление будет отмечено как прочитанное.
    - **is_hidden**: Если передано `True`, уведомление будет скрыто.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    status = await update_notification_status(db, user["id"], notification_id, is_read, is_hidden)
    if not status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return status
