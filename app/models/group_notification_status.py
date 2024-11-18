from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class GroupNotificationStatus(Base):
    __tablename__ = "group_notification_status"

    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), primary_key=True)
    is_read = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)

    group = relationship("Group", back_populates="notification_statuses")
    notification = relationship("Notification", back_populates="group_statuses")