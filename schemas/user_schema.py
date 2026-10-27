from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=40)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: EmailStr = Field(..., description="Correo electrónico")
    password: str = Field(..., min_length=8, max_length=72, description="Contraseña (mínimo 8 caracteres)")


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=40)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    profile_pic: Optional[str] = None
    
    class Config:
        from_attributes = True  # Permite convertir modelos SQLModel a Pydantic

"""
# schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


#OJO MUCHAHCONES
#LOS "..." SE LLAMAN ELIPSIS Y SIGNIFICAN QUE EL CAMPO ES OBLIGATORIO. SI NO PONES LOS "..." EL CAMPO SERÁ OPCIONAL.

# === Esquemas para CREAR usuario ===
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: EmailStr = Field(..., description="Correo electrónico")
    password: str = Field(..., min_length=8, max_length=72, description="Contraseña (mínimo 8 caracteres)")



# === Esquemas para ACTUALIZAR usuario ===


¿UserUpdate puede tener campos que no están en UserCreate?
Sí, absolutamente. 

La regla es:
UserCreate: Solo los campos necesarios para crear (los que el usuario DEBE proporcionar)
UserUpdate: Cualquier campo que pueda cambiar (aunque no se haya usado en Create)
Ambos: Deben existir en el modelo SQLModel (User)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    is_active: Optional[bool] = None
    profile_pic: Optional[str] = None

# === Esquema de RESPUESTA (lo que devuelve la API) ===

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    profile_pic: Optional[str] = None
    
    class Config:
        from_attributes = True  # Permite convertir modelos SQLModel a Pydantic
        
"""