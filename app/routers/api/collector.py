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
@router.post("/collectors", response_model=CollectorRead, status_code=status.HTTP_201_CREATED)
async def create_collector_endpoint(
    collector_data: CollectorCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_user_depend)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return await create_collector(db, user["id"], collector_data)

# Get collectors for the authenticated user
@router.get("/collectors", response_model=list[CollectorRead])
async def get_collectors_endpoint(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_user_depend)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return await get_collectors_by_user(db, user["id"])

# Update a collector by ID
@router.put("/collectors/{collector_id}", response_model=CollectorRead)
async def update_collector_endpoint(
    collector_id: int,
    collector_data: CollectorCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_user_depend)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    collector = await update_collector(db, collector_id, collector_data)
    if not collector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collector not found")
    return collector

# Delete a collector by ID
@router.delete("/collectors/{collector_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collector_endpoint(
    collector_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_user_depend)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    success = await delete_collector(db, collector_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collector not found")
