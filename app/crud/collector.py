from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.collector import (
    create_collector,
    get_collectors_by_user,
    update_collector,
    delete_collector
)
from app.schemas.collector import CollectorCreate, CollectorRead
from app.routers.dependencies.auth import get_user_depend

router = APIRouter()

# Create a collector
@router.post(
    "/collectors",
    response_model=CollectorRead,
    status_code=status.HTTP_201_CREATED,
    tags=["collector"],
    summary="Создать нового сборщика",
    description="Создаёт нового сборщика, связанного с текущим авторизованным пользователем. Доступно только для авторизованных пользователей.",
    responses={
        201: {
            "description": "Сборщик успешно создан",
            "content": {
                "application/json": {
                    "example": CollectorRead.example()
                }
            }
        },
        401: {
            "description": "Неавторизованная попытка создания сборщика",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        }
    }
)
async def create_collector_endpoint(
    collector_data: CollectorCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_user_depend)
):
    """
    Создает нового сборщика для авторизованного пользователя.

    - **collector_data**: Данные для создания сборщика, такие как название, тип клиента и плагин.
    - **user**: Авторизованный пользователь, к которому будет привязан сборщик.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return await create_collector(db, user["id"], collector_data)


# Get collectors for the authenticated user
@router.get(
    "/collectors",
    response_model=list[CollectorRead],
    summary="Получить список сборщиков",
    tags=["collector"],
    description="Возвращает все сборщики, связанные с текущим авторизованным пользователем.",
    responses={
        200: {
            "description": "Список сборщиков пользователя",
            "content": {
                "application/json": {
                    "example": [CollectorRead.example()]
                }
            }
        },
        401: {
            "description": "Неавторизованная попытка получения списка сборщиков",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        }
    }
)
async def get_collectors_endpoint(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_user_depend)
):
    """
    Возвращает список сборщиков, принадлежащих текущему пользователю.

    - **user**: Текущий авторизованный пользователь.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return await get_collectors_by_user(db, user["id"])


# Update a collector by ID
@router.put(
    "/collectors/{collector_id}",
    response_model=CollectorRead,
    summary="Обновить сборщика",
    tags=["collector"],
    description="Обновляет информацию о сборщике по ID. Доступно только для авторизованных пользователей.",
    responses={
        200: {
            "description": "Сборщик успешно обновлен",
            "content": {
                "application/json": {
                    "example": CollectorRead.example()
                }
            }
        },
        401: {
            "description": "Неавторизованная попытка обновления сборщика",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        },
        404: {
            "description": "Сборщик не найден",
            "content": {
                "application/json": {
                    "example": {"detail": "Collector not found"}
                }
            }
        }
    }
)
async def update_collector_endpoint(
    collector_id: int,
    collector_data: CollectorCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_user_depend)
):
    """
    Обновляет данные сборщика, принадлежащего текущему пользователю.

    - **collector_id**: ID сборщика, который требуется обновить.
    - **collector_data**: Новые данные сборщика.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    collector = await update_collector(db, collector_id, collector_data)
    if not collector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collector not found")
    return collector


# Delete a collector by ID
@router.delete(
    "/collectors/{collector_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["collector"],
    summary="Удалить сборщика",
    description="Удаляет сборщика по его ID. Доступно только для авторизованных пользователей.",
    responses={
        204: {
            "description": "Сборщик успешно удалён",
        },
        401: {
            "description": "Неавторизованная попытка удаления сборщика",
            "content": {
                "application/json": {
                    "example": {"detail": "Unauthorized"}
                }
            }
        },
        404: {
            "description": "Сборщик не найден",
            "content": {
                "application/json": {
                    "example": {"detail": "Collector not found"}
                }
            }
        }
    }
)
async def delete_collector_endpoint(
    collector_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_user_depend)
):
    """
    Удаляет сборщика по его ID для текущего пользователя.

    - **collector_id**: ID сборщика, который требуется удалить.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    success = await delete_collector(db, collector_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collector not found")
