from decimal import Decimal
from sqlalchemy import Column, Numeric, Text
from sqlmodel import Field, SQLModel


class Location(SQLModel, table=True):
    __tablename__ = "locations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    label: str = Field(max_length=120)
    latitude: Decimal = Field(sa_column=Column(Numeric(9, 6), nullable=False))
    longitude: Decimal = Field(sa_column=Column(Numeric(9, 6), nullable=False))
    address: str = Field(sa_column=Column(Text, nullable=False))
    geofence_radius_m: int = Field(gt=0)
    is_primary: bool = Field(default=False)