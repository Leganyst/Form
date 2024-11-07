from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    vk_id: str = Field(..., description="ID пользователя во ВКонтакте")
    phone: Optional[str] = Field(None, description="Номер телефона пользователя")

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    collector_count: int = Field(0, description="Количество сборщиков, связанных с пользователем")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls):
        return cls(
            id=1,
            vk_id="user_12345",
            phone="+1234567890",
            collector_count=2
        )
