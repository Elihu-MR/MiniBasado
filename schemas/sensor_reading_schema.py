from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class SensorReadingBase(BaseModel):
    sensor_id: int
    value: Decimal
    unit: str = Field(max_length=30)
    threshold_alert: bool = False
    alert_message: str | None = None


class SensorReadingCreate(SensorReadingBase):
    pass


class SensorReadingUpdate(BaseModel):
    sensor_id: int | None = None
    value: Decimal | None = None
    unit: str | None = Field(default=None, max_length=30)
    threshold_alert: bool | None = None
    alert_message: str | None = None
    recorded_at: datetime | None = None


class SensorReadingResponse(SensorReadingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recorded_at: datetime