from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.refrigerator_model import Refrigerator
from schemas.refrigerator_schema import RefrigeratorCreate, RefrigeratorResponse, RefrigeratorUpdate


router = APIRouter(prefix="/refrigerators", tags=["Refrigerators"])


@router.post("/", response_model=RefrigeratorResponse, status_code=status.HTTP_201_CREATED)
def create_refrigerator(payload: RefrigeratorCreate, session: Session = Depends(get_session)):
    refrigerator = Refrigerator.model_validate(payload)
    session.add(refrigerator)
    try:
        session.commit()
        session.refresh(refrigerator)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario indicado no existe") from error
    return refrigerator


@router.get("/", response_model=list[RefrigeratorResponse])
def get_refrigerators(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(Refrigerator).offset(offset).limit(limit)).all()


@router.get("/{refrigerator_id}", response_model=RefrigeratorResponse)
def get_refrigerator(refrigerator_id: int, session: Session = Depends(get_session)):
    refrigerator = session.get(Refrigerator, refrigerator_id)
    if refrigerator is None:
        raise HTTPException(status_code=404, detail="Refrigerador no encontrado")
    return refrigerator


@router.put("/{refrigerator_id}", response_model=RefrigeratorResponse)
def update_refrigerator(
    refrigerator_id: int,
    payload: RefrigeratorUpdate,
    session: Session = Depends(get_session),
):
    refrigerator = session.get(Refrigerator, refrigerator_id)
    if refrigerator is None:
        raise HTTPException(status_code=404, detail="Refrigerador no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(refrigerator, field, value)
    try:
        session.add(refrigerator)
        session.commit()
        session.refresh(refrigerator)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario indicado no existe") from error
    return refrigerator


@router.delete("/{refrigerator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_refrigerator(refrigerator_id: int, session: Session = Depends(get_session)):
    refrigerator = session.get(Refrigerator, refrigerator_id)
    if refrigerator is None:
        raise HTTPException(status_code=404, detail="Refrigerador no encontrado")
    try:
        session.delete(refrigerator)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: hay registros relacionados") from error