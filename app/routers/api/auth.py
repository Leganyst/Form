from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db 
from app.crud.group import create_group
from app.schemas.group import GroupCreate, GroupRead
from app.routers.dependencies.auth import get_query_params, get_group_depend

router = APIRouter()

@router.get(
    "/auth",
    response_model=GroupRead,
    status_code=status.HTTP_200_OK,
    summary="Аутентификация пользователя",
    description=(
        "Эндпоинт для аутентификации пользователя через VK. "
        "Если пользователь не существует в базе данных, создается новый."
    ),
    responses={
        200: {
            "description": "Успешная аутентификация",
            "content": {
                "application/json": {
                    "example": GroupRead.example()
                }
            }
        },
        401: {
            "description": "Неверный токен аутентификации",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        400: {
            "description": "Некорректный запрос",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            }
        }
    }
)
async def auth_group(group: GroupRead = Depends(get_group_depend), session: AsyncSession = Depends(get_db),
                    group_data: dict = Depends(get_query_params)):
    """
    Аутентифицирует группу на основе предоставленного токена VK.

    - **group**: Объект группы, полученный из зависимости `get_group_depend`.
    - **session**: Сессия базы данных.

    Если пользователь не найден в базе данных, создается новый пользователь.
    Можно использовать как GetMe ручку, для получения обновленной информации о пользователе.
    """
    if not group:
        group = await create_group(session, GroupCreate(
            vk_id=group_data.get("vk_group_id"),
            phone=None
        ))
    return group
