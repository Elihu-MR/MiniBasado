from typing import Any
from pydantic import BaseModel, ConfigDict

from models.enums import FoodImageType


class FoodImageBase(BaseModel):
    food_id: int
    ticket_id: int | None = None
    image_url: str
    image_type: FoodImageType
    ocr_extracted_text: str | None = None
    ai_analysis: dict[str, Any] | None = None


class FoodImageCreate(FoodImageBase):
    pass


class FoodImageUpdate(BaseModel):
    food_id: int | None = None
    ticket_id: int | None = None
    image_url: str | None = None
    image_type: FoodImageType | None = None
    ocr_extracted_text: str | None = None
    ai_analysis: dict[str, Any] | None = None


class FoodImageResponse(FoodImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int