# models/user_model.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.todo_model import Refrigerador

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=3, max_length=50)
    email: str = Field(index=True, unique=True)
    hashed_password: str = Field(min_length=8)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # <-- relación inversa que faltaba
    refrigeradores: List["Refrigerador"] = Relationship(back_populates="usuario")

    class Config:
        table_name = "users"