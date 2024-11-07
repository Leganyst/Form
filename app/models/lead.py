from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=True)
    vk_id = Column(String, nullable=True)
    full_name = Column(String, nullable=False)

    collector_leads = relationship("CollectorLead", back_populates="lead")
