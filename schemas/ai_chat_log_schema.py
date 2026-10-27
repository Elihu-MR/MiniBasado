from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from models.enums import ChatRole


class AIChatLogBase(BaseModel):
    user_id: int
    refrigerator_id: int
    role: ChatRole
    message: str
    attached_image_url: str | None = None
    ai_action_taken: dict[str, Any] | None = None
    tokens_used: int = Field(default=0, ge=0)


class AIChatLogCreate(AIChatLogBase):
    pass


class AIChatLogUpdate(BaseModel):
    user_id: int | None = None
    refrigerator_id: int | None = None
    role: ChatRole | None = None
    message: str | None = None
    attached_image_url: str | None = None
    ai_action_taken: dict[str, Any] | None = None
    tokens_used: int | None = Field(default=None, ge=0)


class AIChatLogResponse(AIChatLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime