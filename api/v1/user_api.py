# api/v1/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from db.database import get_session
from models.user_model import User
from schemas.user_schema import UserCreate, UserUpdate, UserResponse

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta
import boto3

# Importaciones del proyecto
from db.database import get_session
from models.user_model import User
from schemas.user_schema import UserCreate, UserUpdate, UserResponse
from schemas. token_schema import Token, TokenData
from core.security import verify_password, create_access_token, get_password_hash
from core.config import settings
from api.v1.dependencies import get_current_user, get_minio_client, ensure_bucket_exists

import uuid
import os
from botocore.exceptions import ClientError


router = APIRouter()

# === CREAR User ===
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """
    Crea un nuevo User en la base de datos.
    """
    # Verificar si el email ya existe
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar si el username ya existe
    statement = select(User).where(User.username == user_data.username)
    existing_username = session.exec(statement).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya está en uso"
        )
    
    # Crear el User (en producción, hashear la contraseña con bcrypt)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),  # Aquí deberías hashear la contraseña antes de guardarla
        is_active=True
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user

 # === OBTENER todos los Users ===
@router.get("/", response_model=List[UserResponse])
def get_user(
    session: Session = Depends(get_session),          # <-- conexión a la BD
    current_user: User = Depends(get_current_user)  # <-- si quieres proteger el endpoint
):
    """
    Obtiene todos los Users registrados.
    """
    users = session.exec(select(User)).all()
    return users



@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),          # <-- conexión a la BD
    current_user: User = Depends(get_current_user)  # <-- si quieres proteger el endpoint
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User con ID {user_id} no encontrado")
    return user

# === ACTUALIZAR User ===
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    session: Session = Depends(get_current_user)
):
    """
    Actualiza los datos de un User existente.
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User con ID {user_id} no encontrado"
        )
    
    # Actualizar solo los campos que vienen en el request
    update_data = user_update.model_dump(exclude_unset=True) #"truco de magia" para permitir actualizaciones parciales (cuando el cliente solo quiere cambiar uno o dos campos, no todo el registro).


    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user

# === ELIMINAR User ===
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_current_user)):
    """
    Elimina un User de la base de datos.
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User con ID {user_id} no encontrado"
        )
    
    session.delete(db_user)
    session.commit()
    
    return None  # 204 No Content no devuelve nada


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):

    statement = select(User).where(User.username == form_data. username)
    user = session.exec(statement).first()

    if not user or not verify_password( form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}



@router.patch("/me/profile-pic", response_model=UserResponse)
async def update_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    minio_client: boto3.client = Depends(get_minio_client)
):
    # 1. Validar tipo de archivo
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=400, 
            detail="Solo se permiten imágenes JPEG, PNG o WebP"
        )

    # 2. Asegurar que el bucket existe
    ensure_bucket_exists(minio_client)

    try:
        # 3. Generar nombre único y subir a MinIO
        file_extension = os.path.splitext(file.filename)[1] or ".jpg"
        unique_filename = f"profile_{current_user.id}_{uuid.uuid4()}{file_extension}"
    
        minio_client.upload_fileobj(
            file.file,
            settings.MINIO_BUCKET_NAME,
            unique_filename,
            ExtraArgs={'ContentType': file.content_type}
        )

        # 4. Actualizar la referencia en la Base de Datos
        current_user.profile_pic = unique_filename
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return current_user

    except ClientError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al subir la imagen a MinIO: {str(e)}"
        )
