from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.sensor_reading_model import SensorReading
from schemas.sensor_reading_schema import SensorReadingCreate, SensorReadingResponse, SensorReadingUpdate


router = APIRouter(prefix="/sensor-readings", tags=["Sensor readings"])


@router.post("/", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
def create_sensor_reading(payload: SensorReadingCreate, session: Session = Depends(get_session)):
    reading = SensorReading.model_validate(payload)
    session.add(reading)
    try:
        session.commit()
        session.refresh(reading)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El sensor indicado no existe") from error
    return reading


@router.get("/", response_model=list[SensorReadingResponse])
def get_sensor_readings(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(SensorReading).offset(offset).limit(limit)).all()


@router.get("/{reading_id}", response_model=SensorReadingResponse)
def get_sensor_reading(reading_id: int, session: Session = Depends(get_session)):
    reading = session.get(SensorReading, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Lectura no encontrada")
    return reading


@router.put("/{reading_id}", response_model=SensorReadingResponse)
def update_sensor_reading(
    reading_id: int,
    payload: SensorReadingUpdate,
    session: Session = Depends(get_session),
):
    reading = session.get(SensorReading, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Lectura no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(reading, field, value)
    try:
        session.add(reading)
        session.commit()
        session.refresh(reading)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El sensor indicado no existe") from error
    return reading


@router.delete("/{reading_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sensor_reading(reading_id: int, session: Session = Depends(get_session)):
    reading = session.get(SensorReading, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Lectura no encontrada")
    session.delete(reading)
    session.commit()