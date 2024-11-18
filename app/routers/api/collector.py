from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.collector import (
    create_collector,
    get_collectors_by_group,
    update_collector,
    delete_collector,
    get_collector_by_id
)
from app.models.group import Group
from app.schemas.collector import CollectorCreate, CollectorRead, CollectorReadWithVkId
from app.routers.dependencies.auth import get_group_depend
from app.schemas.group import GroupRead
from app.schemas.analytics import CollectorAnalytics
from app.crud.collector import get_collector_analytics

router = APIRouter()

# Create a collector
@router.post(
    "/collectors",
    response_model=CollectorRead,
    status_code=status.HTTP_201_CREATED,
    tags=["collector"],
    summary="Создать нового сборщика",
    description="Создаёт нового сборщика, связанного с текущей авторизованной группой. Только для авторизованных групп",
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
    group: GroupRead = Depends(get_group_depend)
):
    """
    Создает нового сборщика для авторизованной группы.

    - **collector_data**: Данные для создания сборщика, такие как название, тип клиента и плагин.
    - **group**: Авторизованная группа, к которой будет привязан сборщик.
    """
    if not group:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return await create_collector(db, group.id, collector_data)


# Get collectors for the authenticated group
@router.get(
    "/collectors",
    response_model=list[CollectorRead],
    summary="Получить список сборщиков",
    tags=["collector"],
    description="Возвращает все сборщики, связанные с текущей авторизованной группой.",
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
    group: GroupRead = Depends(get_group_depend)
):
    """
    Возвращает список сборщиков, принадлежащих текущей группе.

    - **group**: Текущая авторизованная группа.
    """
    if not group:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return await get_collectors_by_group(db, group.id)


# Update a collector by ID
@router.put(
    "/collectors/{collector_id}",
    response_model=CollectorRead,
    tags=["collector"],
    summary="Обновить сборщика",
    description="Обновляет информацию о сборщике по ID. Доступно только автризованных групп .",
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
    group: GroupRead = Depends(get_group_depend)
):
    """
    Обновляет данные сборщика, принадлежащего текущему пользователю.

    - **collector_id**: ID сборщика, который требуется обновить.
    - **collector_data**: Новые данные сборщика.
    """
    if not group:
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
    group: GroupRead = Depends(get_group_depend)
):
    """
    Удаляет сборщика по его ID для текущей группы.
 
    - **collector_id**: ID сборщика, который требуется удалить.
    """
    if not group:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    success = await delete_collector(db, collector_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collector not found")



@router.get(
    "/{collector_id}",
    response_model=CollectorReadWithVkId,
    summary="Получение информации о коллекторе",
    description="Возвращает полные данные о коллекторе по указанному идентификатору.",
    response_description="Подробная информация о коллекторе",
    status_code=status.HTTP_200_OK,
    tags=["collector"]
)
async def get_collector(collector_id: int, session: AsyncSession = Depends(get_db), group: GroupRead = Depends(get_group_depend)):
    """
    Эндпоинт для получения информации о конкретном коллекторе по его идентификатору.
    """
    collector = await get_collector_by_id(session, collector_id)
    if collector is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collector not found"
        )
    return collector


# Эндпоинт для получения аналитики по коллектору
@router.get(
    "/collectors/{collector_id}/analytics",
    response_model=CollectorAnalytics,
    tags=["collector"],
    summary="Получить аналитику по сборщику",
    description="Возвращает количество лидов, посетителей и CR для указанного сборщика.",
    responses={
        200: {
            "description": "Аналитика успешно получена",
            "content": {
                "application/json": {
                    "example": CollectorAnalytics.example()
                }
            }
        },
        401: {
            "description": "Неавторизованная попытка получения аналитики",
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
async def get_collector_analytics_endpoint(
    collector_id: int,
    db: AsyncSession = Depends(get_db),
    group: GroupRead = Depends(get_group_depend)
):
    """
    Эндпоинт для получения аналитики по коллектору.
    
    - **collector_id**: ID коллектора, по которому требуется аналитика.
    """
    if not group:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    analytics = await get_collector_analytics(db, collector_id)
    if analytics is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collector not found")
    return analytics
