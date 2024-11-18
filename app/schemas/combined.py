from pydantic import BaseModel, Field, ConfigDict
from typing import List
from .group import GroupRead
from .collector import CollectorRead
from .lead import LeadRead
from typing import Optional
from datetime import datetime

class GroupWithCollectors(BaseModel):
    group: GroupRead = Field(..., description="Информация о пользователе")
    collectors: List[CollectorRead] = Field(..., description="Список сборщиков, связанных с пользователем")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls):
        return cls(
            group=GroupRead.example(),
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


class CollectorLeadRead(BaseModel):
    collector_id: int = Field(..., description="ID коллектора")
    lead_id: int = Field(..., description="ID лида")
    checked_form: bool = Field(..., description="Флаг, указывающий, что лид перешел по ссылке на коллектор")
    request_form: bool = Field(..., description="Флаг, указывающий, что лид отправил заявку")
    datetime_request: Optional[datetime] = Field(None, description="Дата и время отправки заявки, если отправлена")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls):
        return cls(
            collector_id=1,
            lead_id=1,
            checked_form=True,
            request_form=True,
            datetime_request=datetime.utcnow()
        )