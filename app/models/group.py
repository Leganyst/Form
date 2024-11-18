# app/models/group.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    vk_id = Column(String, unique=True, nullable=True)
    collector_count = Column(Integer, default=0)
    
    collectors = relationship("Collector", back_populates="group")
    notification_statuses = relationship("GroupNotificationStatus", back_populates="group")
