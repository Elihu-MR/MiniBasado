from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.sensor_model import Sensor
from schemas.sensor_schema import SensorCreate, SensorResponse, SensorUpdate


router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.post("/", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
def create_sensor(payload: SensorCreate, session: Session = Depends(get_session)):
    sensor = Sensor.model_validate(payload)
    session.add(sensor)
    try:
        session.commit()
        session.refresh(sensor)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario o refrigerador indicado no existe") from error
    return sensor


@router.get("/", response_model=list[SensorResponse])
def get_sensors(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(Sensor).offset(offset).limit(limit)).all()


@router.get("/{sensor_id}", response_model=SensorResponse)
def get_sensor(sensor_id: int, session: Session = Depends(get_session)):
    sensor = session.get(Sensor, sensor_id)
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return sensor


@router.put("/{sensor_id}", response_model=SensorResponse)
def update_sensor(sensor_id: int, payload: SensorUpdate, session: Session = Depends(get_session)):
    sensor = session.get(Sensor, sensor_id)
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(sensor, field, value)
    try:
        session.add(sensor)
        session.commit()
        session.refresh(sensor)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario o refrigerador indicado no existe") from error
    return sensor


@router.delete("/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sensor(sensor_id: int, session: Session = Depends(get_session)):
    sensor = session.get(Sensor, sensor_id)
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    try:
        session.delete(sensor)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: hay cámaras o lecturas relacionadas") from error