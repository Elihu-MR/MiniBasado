from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CameraBase(BaseModel):
    sensor_id: int
    user_id: int
    ip_address: str = Field(max_length=45)
    mac_address: str = Field(max_length=17)
    is_recording: bool = False
    storage_path: str


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    sensor_id: int | None = None
    user_id: int | None = None
    ip_address: str | None = Field(default=None, max_length=45)
    mac_address: str | None = Field(default=None, max_length=17)
    is_recording: bool | None = None
    storage_path: str | None = None


class CameraResponse(CameraBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime