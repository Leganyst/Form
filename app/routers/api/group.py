from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.group import GroupCreate, GroupRead
from app.crud.group import (
    create_group,
    get_group_by_id,
    get_group_by_vk_id,
    update_group,
    delete_group
)
from app.core.database import get_db

router = APIRouter()

# Create group

@router.post("/group", response_model=GroupRead, status_code=status.HTTP_201_CREATED, tags=["group"])
async def create_group_endpoint(group_data: GroupCreate, db: AsyncSession = Depends(get_db)):
    return await create_group(db, group_data)

# Get group by ID
@router.get("/group/{group_id}", response_model=GroupRead, tags=["group"])
async def get_group_by_id_endpoint(group_id: int, db: AsyncSession = Depends(get_db)):
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="group not found")
    return group

# Get group by VK ID
@router.get("/group/vk/{vk_id}", response_model=GroupRead, tags=["group"])
async def get_group_by_vk_id_endpoint(vk_id: str, db: AsyncSession = Depends(get_db)):
    group = await get_group_by_vk_id(db, vk_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="group not found")
    return group

# Update group
@router.put("/group/{group_id}", response_model=GroupRead, tags=["group"])
async def update_group_endpoint(group_id: int, group_data: GroupCreate, db: AsyncSession = Depends(get_db)):
    group = await update_group(db, group_id, group_data)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="group not found")
    return group

# Delete group
@router.delete("/group/{group_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["group"])
async def delete_group_endpoint(group_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_group(db, group_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="group not found")
