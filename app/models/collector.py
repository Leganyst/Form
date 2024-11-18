from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

import enum

class ClientPathType(enum.Enum):
    MESSENGER = "messenger"
    SUBSCRIPTION = "subscription"
    CHAT_BOT = "chat_bot"

class PluginType(enum.Enum):
    SENLER = "senler"
    VKONTAKTE = "vkontakte"
    BOTHELPER = "bothelper"

class Collector(Base):
    __tablename__ = "collectors"

    id = Column(Integer, primary_key=True)
    name = Column(String, default="сборщик", nullable=False)
    transcription = Column(String, nullable=True)
    description = Column(String, nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    client_path_type = Column(Enum(ClientPathType), nullable=False)
    client_path = Column(Text, nullable=True)
    plugin = Column(Enum(PluginType), nullable=True)
    count_leads = Column(Integer, default=0)
    request_phone_numbers = Column(Boolean, default=False)
    first_bonus = Column(String(50), nullable=True)
    second_bonus = Column(String(50), nullable=True)
    third_bonus = Column(String(50), nullable=True)
    
    group = relationship("Group", back_populates="collectors")
    collector_leads = relationship("CollectorLead", back_populates="collector")