from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class NotificationBase(BaseModel):
    title: str = Field(..., description="Название уведомления")
    description: str = Field(..., description="Краткое описание уведомления")
    link: Optional[str] = Field(None, description="Ссылка, связанная с уведомлением")
    notification_type: str = Field(..., description="Тип уведомления ('system', 'news' и т.д.) (system нельзя закрыть, news - можно)")

class NotificationCreate(NotificationBase):
    pass

class NotificationRead(NotificationBase):
    id: int = Field(..., description="Уникальный идентификатор уведомления")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls):
        return cls(
            id=1,
            title="New Feature Released",
            description="Check out our new feature...",
            link="https://example.com",
            notification_type="news"
        )
