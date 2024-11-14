from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class LeadBase(BaseModel):
    phone: Optional[str] = Field(None, description="Номер телефона лида")
    vk_id: Optional[str] = Field(None, description="ID лида во ВКонтакте")
    full_name: str = Field(..., description="Полное имя лида")
    request_form: bool = Field(..., description="Заполнена ли форма заявки")
    request_datetime: str = Field(..., description="Дата и время получения заявки")

class LeadCreate(LeadBase):
    pass

class LeadRead(LeadBase):
    id: int = Field(..., description="Уникальный идентификатор лида")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls):
        return cls(
            id=1,
            phone="+1234567890",
            vk_id="lead_67890",
            full_name="John Doe",
            request_form="True",
            request_datetime="2021-10-10 10:10:10"
        )
