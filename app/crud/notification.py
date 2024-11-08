from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.models.notification import Notification
from app.models.user_notification_status import UserNotificationStatus
from app.schemas.notification import NotificationCreate, NotificationRead
from app.schemas.user_notification_status import UserNotificationStatusRead

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

# Get notifications for a user
async def get_notifications_for_user(db: AsyncSession, user_id: int) -> list[NotificationRead]:
    result = await db.execute(
        select(Notification)
        .join(UserNotificationStatus)
        .filter(UserNotificationStatus.user_id == user_id)
    )
    notifications = result.scalars().all()
    return [NotificationRead.model_validate(n) for n in notifications]

# Update notification status for user (mark as read or hidden)
async def update_notification_status(
    db: AsyncSession, user_id: int, notification_id: int, is_read: bool = None, is_hidden: bool = None
) -> UserNotificationStatusRead:
    values = {}
    if is_read is not None:
        values["is_read"] = is_read
    if is_hidden is not None:
        values["is_hidden"] = is_hidden

    result = await db.execute(
        update(UserNotificationStatus)
        .where(UserNotificationStatus.user_id == user_id, UserNotificationStatus.notification_id == notification_id)
        .values(**values)
        .returning(UserNotificationStatus)
    )
    status = result.scalar_one_or_none()
    await db.commit()
    return UserNotificationStatusRead.model_validate(status) if status else None
