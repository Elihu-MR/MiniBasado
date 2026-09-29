# schemas/token_schema.py
from pydantic import BaseModel
from typing import Optional
from sqlmodel import SQLModel
from jose import JWTError, jwt


class Token(BaseModel) :
    access_token: str
    token_type: str

class TokenData(BaseModel) :
    jwt.username: str | None = None