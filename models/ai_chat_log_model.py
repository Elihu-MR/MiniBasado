from datetime import datetime
from typing import Any
from sqlalchemy import Column, JSON, Enum as SAEnum, Text
from sqlmodel import Field, SQLModel

from models.common import utc_now
from models.enums import ChatRole


class AIChatLog(SQLModel, table=True):
    __tablename__ = "ai_chat_logs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    refrigerator_id: int = Field(foreign_key="refrigerators.id", index=True)
    role: ChatRole = Field(sa_column=Column(SAEnum(ChatRole, name="chat_role_enum"), nullable=False))
    message: str = Field(sa_column=Column(Text, nullable=False))
    attached_image_url: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    ai_action_taken: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    tokens_used: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utc_now)