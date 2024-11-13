from pydantic import BaseModel, Field

class CollectorAnalytics(BaseModel):
    collector_id: int = Field(..., description="ID коллектора")
    leads_count: int = Field(..., description="Количество лидов")
    visit_count: int = Field(..., description="Количество посетителей без заявок")
    conversion_rate: float = Field(..., description="Конверсия в процентах (CR)")

    @classmethod
    def example(cls):
        return cls(
            collector_id=1,
            leads_count=50,
            visit_count=200,
            conversion_rate=25.0
        )
