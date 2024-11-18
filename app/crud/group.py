from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupRead

# Create
async def create_group(db: AsyncSession, group_data: GroupCreate) -> GroupRead:
    group = Group(vk_id=group_data.vk_id)
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return GroupRead.model_validate(group)

# Read by ID
async def get_group_by_id(db: AsyncSession, group_id: int) -> GroupRead:
    result = await db.execute(select(Group).filter(Group.id == group_id))
    group = result.scalars().first()
    return GroupRead.model_validate(group) if group else None

# Read by VK ID
async def get_group_by_vk_id(db: AsyncSession, vk_id: str) -> GroupRead:
    result = await db.execute(select(Group).filter(Group.vk_id == vk_id))
    group = result.scalars().first()
    return GroupRead.model_validate(group) if group else None

# Update
async def update_group(db: AsyncSession, group_id: int, group_data: GroupCreate) -> GroupRead:
    result = await db.execute(
        update(Group)
        .where(Group.id == group_id)
        .values(vk_id=group_data.vk_id, phone=group_data.phone)
        .returning(Group)
    )
    group = result.scalar_one_or_none()
    await db.commit()
    return GroupRead.model_validate(group) if group else None

# Delete
async def delete_group(db: AsyncSession, group_id: int) -> bool:
    result = await db.execute(delete(Group).where(Group.id == group_id))
    await db.commit()
    return result.rowcount > 0
