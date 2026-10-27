from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.camera_event_model import CameraEvent
from schemas.camera_event_schema import CameraEventCreate, CameraEventResponse, CameraEventUpdate


router = APIRouter(prefix="/camera-events", tags=["Camera events"])


@router.post("/", response_model=CameraEventResponse, status_code=status.HTTP_201_CREATED)
def create_camera_event(payload: CameraEventCreate, session: Session = Depends(get_session)):
    event = CameraEvent.model_validate(payload)
    session.add(event)
    try:
        session.commit()
        session.refresh(event)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="La cámara indicada no existe") from error
    return event


@router.get("/", response_model=list[CameraEventResponse])
def get_camera_events(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(CameraEvent).offset(offset).limit(limit)).all()


@router.get("/{event_id}", response_model=CameraEventResponse)
def get_camera_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(CameraEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event


@router.put("/{event_id}", response_model=CameraEventResponse)
def update_camera_event(
    event_id: int,
    payload: CameraEventUpdate,
    session: Session = Depends(get_session),
):
    event = session.get(CameraEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    try:
        session.add(event)
        session.commit()
        session.refresh(event)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="La cámara indicada no existe") from error
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(CameraEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    session.delete(event)
    session.commit()