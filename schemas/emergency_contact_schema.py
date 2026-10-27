from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EmergencyContactBase(BaseModel):
    user_id: int
    location_id: int
    name: str = Field(max_length=120)
    relationship: str = Field(max_length=80)
    phone_primary: str = Field(max_length=40)
    phone_secondary: str | None = Field(default=None, max_length=40)
    priority: int = Field(ge=1)
    is_active: bool = True


class EmergencyContactCreate(EmergencyContactBase):
    pass


class EmergencyContactUpdate(BaseModel):
    user_id: int | None = None
    location_id: int | None = None
    name: str | None = Field(default=None, max_length=120)
    relationship: str | None = Field(default=None, max_length=80)
    phone_primary: str | None = Field(default=None, max_length=40)
    phone_secondary: str | None = Field(default=None, max_length=40)
    priority: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class EmergencyContactResponse(EmergencyContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime