from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.location_model import Location
from schemas.location_schema import LocationCreate, LocationResponse, LocationUpdate


router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(payload: LocationCreate, session: Session = Depends(get_session)):
    location = Location.model_validate(payload)
    session.add(location)
    try:
        session.commit()
        session.refresh(location)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario indicado no existe") from error
    return location


@router.get("/", response_model=list[LocationResponse])
def get_locations(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(Location).offset(offset).limit(limit)).all()


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, session: Session = Depends(get_session)):
    location = session.get(Location, location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    return location


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(location_id: int, payload: LocationUpdate, session: Session = Depends(get_session)):
    location = session.get(Location, location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(location, field, value)
    try:
        session.add(location)
        session.commit()
        session.refresh(location)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario indicado no existe") from error
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, session: Session = Depends(get_session)):
    location = session.get(Location, location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Ubicación no encontrada")
    try:
        session.delete(location)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: hay contactos relacionados") from error