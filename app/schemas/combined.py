from pydantic import BaseModel, Field, ConfigDict
from typing import List
from .user import UserRead
from .collector import CollectorRead
from .lead import LeadRead

class UserWithCollectors(BaseModel):
    user: UserRead = Field(..., description="Информация о пользователе")
    collectors: List[CollectorRead] = Field(..., description="Список сборщиков, связанных с пользователем")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls):
        return cls(
            user=UserRead.example(),
            collectors=[CollectorRead.example()]
        )

class CollectorWithLeads(BaseModel):
    collector: CollectorRead = Field(..., description="Информация о сборщике")
    leads: List[LeadRead] = Field(..., description="Список лидов, связанных с данным сборщиком")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls):
        return cls(
            collector=CollectorRead.example(),
            leads=[LeadRead.example()]
        )
