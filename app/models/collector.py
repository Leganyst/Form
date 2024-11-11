from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

import enum

class ClientPathType(str, Enum):
    MESSENGER = "MESSENGER"
    SUBSCRIPTION = "SUBSCRIPTION"
    CHAT_BOT = "CHAT_BOT"

class PluginType(str, Enum):
    SENLER = "SENLER"
    VKONTAKTE = "VKONTAKTE"
    BOTHELPER = "BOTHELPER"

class Collector(Base):
    __tablename__ = "collectors"

    id = Column(Integer, primary_key=True)
    name = Column(String, default="сборщик", nullable=False)
    transcription = Column(String, nullable=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_path_type = Column(Enum(ClientPathType), nullable=False)
    plugin = Column(Enum(PluginType), nullable=True)
    count_leads = Column(Integer, default=0)
    
    
    user = relationship("User", back_populates="collectors")
    collector_leads = relationship("CollectorLead", back_populates="collector")