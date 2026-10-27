from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Numeric, Text
from sqlmodel import Field, SQLModel

from models.common import utc_now


class SensorReading(SQLModel, table=True):
    __tablename__ = "sensor_readings"

    id: int | None = Field(default=None, primary_key=True)
    sensor_id: int = Field(foreign_key="sensors.id", index=True)
    value: Decimal = Field(sa_column=Column(Numeric(12, 4), nullable=False))
    unit: str = Field(max_length=30)
    threshold_alert: bool = Field(default=False)
    alert_message: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    recorded_at: datetime = Field(default_factory=utc_now)