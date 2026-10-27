from typing import Any
from sqlalchemy import Column, JSON, Enum as SAEnum, Text
from sqlmodel import Field, SQLModel

from models.enums import FoodImageType


class FoodImage(SQLModel, table=True):
    __tablename__ = "food_images"

    id: int | None = Field(default=None, primary_key=True)
    food_id: int = Field(foreign_key="foods.id", index=True)
    ticket_id: int | None = Field(default=None, foreign_key="purchase_tickets.id", index=True)
    image_url: str = Field(sa_column=Column(Text, nullable=False))
    image_type: FoodImageType = Field(sa_column=Column(SAEnum(FoodImageType, name="food_image_type_enum"), nullable=False))
    ocr_extracted_text: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    ai_analysis: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON, nullable=True))