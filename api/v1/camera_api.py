from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.camera_model import Camera
from schemas.camera_schema import CameraCreate, CameraResponse, CameraUpdate


router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.post("/", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
def create_camera(payload: CameraCreate, session: Session = Depends(get_session)):
    camera = Camera.model_validate(payload)
    session.add(camera)
    try:
        session.commit()
        session.refresh(camera)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El sensor o usuario indicado no existe") from error
    return camera


@router.get("/", response_model=list[CameraResponse])
def get_cameras(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(Camera).offset(offset).limit(limit)).all()


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: int, session: Session = Depends(get_session)):
    camera = session.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(camera_id: int, payload: CameraUpdate, session: Session = Depends(get_session)):
    camera = session.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(camera, field, value)
    try:
        session.add(camera)
        session.commit()
        session.refresh(camera)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El sensor o usuario indicado no existe") from error
    return camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(camera_id: int, session: Session = Depends(get_session)):
    camera = session.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    try:
        session.delete(camera)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: hay eventos relacionados") from error