from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

# Importaciones del proyecto
from db.database import get_session
from core.config import settings
from models.user_model import User

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo",
        )
    return current_user


# === Dependencias de MinIO ===

def get_minio_client():
    """Genera y retorna un cliente Boto3 configurado para MinIO."""
    try:
        client = boto3.client(
            "s3",
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name=settings.MINIO_REGION,
        )
        yield client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al conectar con MinIO: {str(e)}",
        )


def ensure_bucket_exists(client: boto3.client):
    """Verifica que el bucket exista, si no, lo crea."""
    try:
        client.head_bucket(Bucket=settings.MINIO_BUCKET_NAME)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            client.create_bucket(Bucket=settings.MINIO_BUCKET_NAME)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al verificar el bucket: {str(e)}",
            )