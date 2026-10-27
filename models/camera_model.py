from datetime import datetime
from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from models.common import utc_now


class Camera(SQLModel, table=True):
    __tablename__ = "cameras"

    id: int | None = Field(default=None, primary_key=True)
    sensor_id: int = Field(foreign_key="sensors.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    ip_address: str = Field(max_length=45)
    mac_address: str = Field(max_length=17)
    is_recording: bool = Field(default=False)
    storage_path: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=utc_now)