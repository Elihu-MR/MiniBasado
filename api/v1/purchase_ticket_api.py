from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.purchase_ticket_model import PurchaseTicket
from schemas.purchase_ticket_schema import PurchaseTicketCreate, PurchaseTicketResponse, PurchaseTicketUpdate


router = APIRouter(prefix="/purchase-tickets", tags=["Purchase tickets"])


@router.post("/", response_model=PurchaseTicketResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_ticket(payload: PurchaseTicketCreate, session: Session = Depends(get_session)):
    ticket = PurchaseTicket.model_validate(payload)
    session.add(ticket)
    try:
        session.commit()
        session.refresh(ticket)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario o refrigerador indicado no existe") from error
    return ticket


@router.get("/", response_model=list[PurchaseTicketResponse])
def get_purchase_tickets(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(PurchaseTicket).offset(offset).limit(limit)).all()


@router.get("/{ticket_id}", response_model=PurchaseTicketResponse)
def get_purchase_ticket(ticket_id: int, session: Session = Depends(get_session)):
    ticket = session.get(PurchaseTicket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket


@router.put("/{ticket_id}", response_model=PurchaseTicketResponse)
def update_purchase_ticket(
    ticket_id: int,
    payload: PurchaseTicketUpdate,
    session: Session = Depends(get_session),
):
    ticket = session.get(PurchaseTicket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    try:
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario o refrigerador indicado no existe") from error
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_purchase_ticket(ticket_id: int, session: Session = Depends(get_session)):
    ticket = session.get(PurchaseTicket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    try:
        session.delete(ticket)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: hay imágenes relacionadas") from error