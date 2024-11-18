from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.models.notification import Notification
from app.models.group_notification_status import GroupNotificationStatus
from app.schemas.notification import NotificationCreate, NotificationRead
from app.schemas.group_notification_status import GroupNotificationStatusRead

# Create notification
async def create_notification(db: AsyncSession, notification_data: NotificationCreate) -> NotificationRead:
    notification = Notification(
        title=notification_data.title,
        description=notification_data.description,
        link=notification_data.link,
        notification_type=notification_data.notification_type,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return NotificationRead.model_validate(notification)

# Get notifications for a group
async def get_notifications_for_group(db: AsyncSession, group_id: int) -> list[NotificationRead]:
    result = await db.execute(
        select(Notification)
        .join(GroupNotificationStatus)
        .filter(GroupNotificationStatus.group == group_id)
    )
    notifications = result.scalars().all()
    return [NotificationRead.model_validate(n) for n in notifications]

# Update notification status for group (mark as read or hidden)
async def update_notification_status(
    db: AsyncSession, group_id: int, notification_id: int, is_read: bool = None, is_hidden: bool = None
) -> GroupNotificationStatusRead:
    values = {}
    
    notification_type = await db.execute(
        select(Notification.notification_type)
        .filter(Notification.id == notification_id)
    )
    
    if is_read is not None:
        values["is_read"] = is_read
        
    if is_hidden is not None and notification_type != "system":
        values["is_hidden"] = is_hidden
    

    result = await db.execute(
        update(GroupNotificationStatus)
        .where(GroupNotificationStatus.group == group_id, GroupNotificationStatus.notification_id == notification_id)
        .values(**values)
        .returning(GroupNotificationStatus)
    )
    status = result.scalar_one_or_none()
    await db.commit()
    return GroupNotificationStatusRead.model_validate(status) if status else None
