from datetime import datetime
from sqlmodel import Field, SQLModel

from models.common import utc_now


class Refrigerator(SQLModel, table=True):
    __tablename__ = "refrigerators"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=120)
    brand: str = Field(max_length=100)
    esp32_device_id: str = Field(max_length=120)
    capacity_liters: int = Field(gt=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)