from datetime import datetime
from sqlalchemy import Column, Enum as SAEnum, Text
from sqlmodel import Field, SQLModel

from models.common import utc_now
from models.enums import SensorType


class Sensor(SQLModel, table=True):
    __tablename__ = "sensors"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    refrigerator_id: int = Field(foreign_key="refrigerators.id", index=True)
    sensor_type: SensorType = Field(sa_column=Column(SAEnum(SensorType, name="sensor_type_enum"), nullable=False))
    name: str = Field(max_length=120)
    esp32_pin: str = Field(max_length=40)
    mqtt_topic: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    last_reading_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)