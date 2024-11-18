from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class GroupBase(BaseModel):
    vk_id: str = Field(..., description="ID пользователя во ВКонтакте")

    model_config = ConfigDict(from_attributes=True)

class GroupCreate(GroupBase):
    pass

class GroupRead(GroupBase):
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    collector_count: int = Field(0, description="Количество сборщиков, связанных с пользователем")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls):
        return cls(
            id=1,
            vk_id="4343242312345",
            collector_count=2
        )
