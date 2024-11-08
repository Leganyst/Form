from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserRead
from app.crud.user import (
    create_user,
    get_user_by_id,
    get_user_by_vk_id,
    update_user,
    delete_user
)
from app.core.database import get_db

router = APIRouter()

# Create User
@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["user"])
async def create_user_endpoint(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user_data)

# Get User by ID
@router.get("/users/{user_id}", response_model=UserRead, tags=["user"])
async def get_user_by_id_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Get User by VK ID
@router.get("/users/vk/{vk_id}", response_model=UserRead, tags=["user"])
async def get_user_by_vk_id_endpoint(vk_id: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_vk_id(db, vk_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Update User
@router.put("/users/{user_id}", response_model=UserRead, tags=["user"])
async def update_user_endpoint(user_id: int, user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Delete User
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["test"])
async def delete_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
