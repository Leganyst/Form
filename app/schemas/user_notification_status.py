from pydantic import BaseModel, Field
from app.schemas.user import UserRead
from app.schemas.notification import NotificationRead

class UserNotificationStatusRead(BaseModel):
    user_id: int = Field(..., description="ID пользователя, связанного с уведомлением")
    notification_id: int = Field(..., description="ID уведомления")
    is_read: bool = Field(default=False, description="Указывает, прочитано ли уведомление")
    is_hidden: bool = Field(default=False, description="Указывает, скрыто ли уведомление")

    class Config:
        orm_mode = True

    @classmethod
    def example(cls):
        return cls(
            user_id=1,
            notification_id=1,
            is_read=True,
            is_hidden=False
        )
