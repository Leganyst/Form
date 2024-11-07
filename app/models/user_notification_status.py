from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserNotificationStatus(Base):
    __tablename__ = "user_notification_status"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), primary_key=True)
    is_read = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)

    user = relationship("User", back_populates="notification_statuses")
    notification = relationship("Notification", back_populates="user_statuses")
