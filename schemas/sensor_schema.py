from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from models.enums import SensorType


class SensorBase(BaseModel):
    user_id: int
    refrigerator_id: int
    sensor_type: SensorType
    name: str = Field(max_length=120)
    esp32_pin: str = Field(max_length=40)
    mqtt_topic: str = Field(max_length=255)
    is_active: bool = True


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    user_id: int | None = None
    refrigerator_id: int | None = None
    sensor_type: SensorType | None = None
    name: str | None = Field(default=None, max_length=120)
    esp32_pin: str | None = Field(default=None, max_length=40)
    mqtt_topic: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    last_reading_at: datetime | None = None


class SensorResponse(SensorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_reading_at: datetime | None
    created_at: datetime