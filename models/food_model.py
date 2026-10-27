from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, Enum as SAEnum, Numeric
from sqlmodel import Field, SQLModel

from models.common import utc_now
from models.enums import FoodStatus


class Food(SQLModel, table=True):
    __tablename__ = "foods"

    id: int | None = Field(default=None, primary_key=True)
    refrigerator_id: int = Field(foreign_key="refrigerators.id", index=True)
    name: str = Field(max_length=120)
    category: str = Field(max_length=80)
    quantity: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    unit: str = Field(max_length=30)
    purchase_date: date
    expiration_date: date
    status: FoodStatus = Field(sa_column=Column(SAEnum(FoodStatus, name="food_status_enum"), nullable=False))
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)