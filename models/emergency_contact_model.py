from datetime import datetime
from sqlmodel import Field, SQLModel

from models.common import utc_now


class EmergencyContact(SQLModel, table=True):
    __tablename__ = "emergency_contacts"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    location_id: int = Field(foreign_key="locations.id", index=True)
    name: str = Field(max_length=120)
    relationship: str = Field(max_length=80)
    phone_primary: str = Field(max_length=40)
    phone_secondary: str | None = Field(default=None, max_length=40)
    priority: int = Field(ge=1)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)