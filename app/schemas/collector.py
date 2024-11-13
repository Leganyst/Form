from httpx import request
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum

class ClientPathType(str, Enum):
    messenger = "messenger"
    subscription = "subscription"
    chat_bot = "chat_bot"

class PluginType(str, Enum):
    senler = "senler"
    vkontakte = "vkontakte"
    bothelper = "bothelper"

class CollectorBase(BaseModel):
    name: str = Field(default="сборщик", description="Название сборщика")
    description: Optional[str] = Field(default="Описание сборщика", description="Описание сборщика")
    transcription: Optional[str] = Field(None, description="Транскрипция названия сборщика")
    client_path_type: ClientPathType = Field(..., description="Тип пути клиента для получения заявок")
    plugin: Optional[PluginType] = Field(None, description="Плагин для интеграции, если выбран способ 'Рассылка'")
    count_leads: Optional[int] = Field(0, description="Количество привлечённых лидов") 
    request_phone_numbers: Optional[bool] = Field(False, description="Запрашивать ли номера телефонов у клиентов")
        
class CollectorCreate(CollectorBase):
    user_id: int = Field(..., description="ID пользователя, к которому привязан сборщик")

class CollectorRead(CollectorBase):
    id: int = Field(..., description="Уникальный идентификатор сборщика")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def example(cls):
        return cls(
            id=1,
            name="Collector A",
            transcription="Collector_1",
            description="Collector_1 desctiption",
            client_path_type=ClientPathType.messenger,
            plugin=PluginType.vkontakte,
            count_leads=0
        )
