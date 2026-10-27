from datetime import datetime
from sqlalchemy import Column, Enum as SAEnum, Text
from sqlmodel import Field, SQLModel

from models.common import utc_now
from models.enums import CameraEventType, EventSeverity


class CameraEvent(SQLModel, table=True):
    __tablename__ = "camera_events"

    id: int | None = Field(default=None, primary_key=True)
    camera_id: int = Field(foreign_key="cameras.id", index=True)
    event_type: CameraEventType = Field(sa_column=Column(SAEnum(CameraEventType, name="camera_event_type_enum"), nullable=False))
    snapshot_url: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    ai_description: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    severity: EventSeverity = Field(sa_column=Column(SAEnum(EventSeverity, name="event_severity_enum"), nullable=False))
    detected_at: datetime = Field(default_factory=utc_now)
    acknowledged: bool = Field(default=False)