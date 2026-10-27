from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.emergency_contact_model import EmergencyContact
from schemas.emergency_contact_schema import EmergencyContactCreate, EmergencyContactResponse, EmergencyContactUpdate


router = APIRouter(prefix="/emergency-contacts", tags=["Emergency contacts"])


@router.post("/", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
def create_emergency_contact(payload: EmergencyContactCreate, session: Session = Depends(get_session)):
    contact = EmergencyContact.model_validate(payload)
    session.add(contact)
    try:
        session.commit()
        session.refresh(contact)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario o ubicación indicada no existe") from error
    return contact


@router.get("/", response_model=list[EmergencyContactResponse])
def get_emergency_contacts(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(EmergencyContact).offset(offset).limit(limit)).all()


@router.get("/{contact_id}", response_model=EmergencyContactResponse)
def get_emergency_contact(contact_id: int, session: Session = Depends(get_session)):
    contact = session.get(EmergencyContact, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contacto de emergencia no encontrado")
    return contact


@router.put("/{contact_id}", response_model=EmergencyContactResponse)
def update_emergency_contact(
    contact_id: int,
    payload: EmergencyContactUpdate,
    session: Session = Depends(get_session),
):
    contact = session.get(EmergencyContact, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contacto de emergencia no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    try:
        session.add(contact)
        session.commit()
        session.refresh(contact)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario o ubicación indicada no existe") from error
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_emergency_contact(contact_id: int, session: Session = Depends(get_session)):
    contact = session.get(EmergencyContact, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contacto de emergencia no encontrado")
    session.delete(contact)
    session.commit()