from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class LeadBase(BaseModel):
    phone: Optional[str] = Field(None, description="Номер телефона лида")
    vk_id: Optional[str] = Field(None, description="ID лида во ВКонтакте")
    full_name: str = Field(..., description="Полное имя лида")

class LeadCreate(BaseModel):
    vk_id: str = Field(..., description="ID лида во ВКонтакте")        

class LeadRead(LeadBase):
    id: int = Field(..., description="Уникальный идентификатор лида")
    photo: Optional[str] = Field(None, description="Ссылка на фото лида")
    
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls):
        return cls(
            id=1,
            phone="+1234567890",
            vk_id="lead_67890",
            full_name="John Doe",
            photo=None
        )
