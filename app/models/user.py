# app/models/user.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    vk_id = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    collector_count = Column(Integer, default=0)
    
    collectors = relationship("Collector", back_populates="user")
    notification_statuses = relationship("UserNotificationStatus", back_populates="user")
