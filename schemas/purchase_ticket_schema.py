from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class PurchaseTicketBase(BaseModel):
    user_id: int
    refrigerator_id: int
    store_name: str = Field(max_length=160)
    purchase_date: date
    ticket_image_url: str | None = None
    raw_text: str | None = None
    processed_at: bool = False


class PurchaseTicketCreate(PurchaseTicketBase):
    pass


class PurchaseTicketUpdate(BaseModel):
    user_id: int | None = None
    refrigerator_id: int | None = None
    store_name: str | None = Field(default=None, max_length=160)
    purchase_date: date | None = None
    ticket_image_url: str | None = None
    raw_text: str | None = None
    processed_at: bool | None = None


class PurchaseTicketResponse(PurchaseTicketBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime