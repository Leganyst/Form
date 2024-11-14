from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class CollectorLead(Base):
    __tablename__ = "collector_lead"

    collector_id = Column(Integer, ForeignKey("collectors.id"), primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), primary_key=True)
    checked_form = Column(Boolean, default=False)
    request_form = Column(Boolean, default=False)
    datetime_request = Column(DateTime, nullable=True)
    # Дополнительные поля могут быть добавлены здесь

    collector = relationship("Collector", back_populates="collector_leads")
    lead = relationship("Lead", back_populates="collector_leads")