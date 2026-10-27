from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from models.enums import FoodStatus


class FoodBase(BaseModel):
    refrigerator_id: int
    name: str = Field(max_length=120)
    category: str = Field(max_length=80)
    quantity: Decimal
    unit: str = Field(max_length=30)
    purchase_date: date
    expiration_date: date
    status: FoodStatus


class FoodCreate(FoodBase):
    pass


class FoodUpdate(BaseModel):
    refrigerator_id: int | None = None
    name: str | None = Field(default=None, max_length=120)
    category: str | None = Field(default=None, max_length=80)
    quantity: Decimal | None = None
    unit: str | None = Field(default=None, max_length=30)
    purchase_date: date | None = None
    expiration_date: date | None = None
    status: FoodStatus | None = None


class FoodResponse(FoodBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime