from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class LocationBase(BaseModel):
    user_id: int
    label: str = Field(max_length=120)
    latitude: Decimal
    longitude: Decimal
    address: str
    geofence_radius_m: int = Field(gt=0)
    is_primary: bool = False


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    user_id: int | None = None
    label: str | None = Field(default=None, max_length=120)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    address: str | None = None
    geofence_radius_m: int | None = Field(default=None, gt=0)
    is_primary: bool | None = None


class LocationResponse(LocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int