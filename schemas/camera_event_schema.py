from datetime import datetime
from pydantic import BaseModel, ConfigDict

from models.enums import CameraEventType, EventSeverity


class CameraEventBase(BaseModel):
    camera_id: int
    event_type: CameraEventType
    snapshot_url: str | None = None
    ai_description: str | None = None
    severity: EventSeverity
    acknowledged: bool = False


class CameraEventCreate(CameraEventBase):
    pass


class CameraEventUpdate(BaseModel):
    camera_id: int | None = None
    event_type: CameraEventType | None = None
    snapshot_url: str | None = None
    ai_description: str | None = None
    severity: EventSeverity | None = None
    detected_at: datetime | None = None
    acknowledged: bool | None = None


class CameraEventResponse(CameraEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    detected_at: datetime