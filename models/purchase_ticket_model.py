from datetime import date, datetime
from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from models.common import utc_now


class PurchaseTicket(SQLModel, table=True):
    __tablename__ = "purchase_tickets"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    refrigerator_id: int = Field(foreign_key="refrigerators.id", index=True)
    store_name: str = Field(max_length=160)
    purchase_date: date
    ticket_image_url: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    raw_text: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    processed_at: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)