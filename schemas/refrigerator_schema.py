from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RefrigeratorBase(BaseModel):
    user_id: int
    name: str = Field(max_length=120)
    brand: str = Field(max_length=100)
    esp32_device_id: str = Field(max_length=120)
    capacity_liters: int = Field(gt=0)
    is_active: bool = True


class RefrigeratorCreate(RefrigeratorBase):
    pass


class RefrigeratorUpdate(BaseModel):
    user_id: int | None = None
    name: str | None = Field(default=None, max_length=120)
    brand: str | None = Field(default=None, max_length=100)
    esp32_device_id: str | None = Field(default=None, max_length=120)
    capacity_liters: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class RefrigeratorResponse(RefrigeratorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime