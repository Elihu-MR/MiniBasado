from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.ai_chat_log_model import AIChatLog
from schemas.ai_chat_log_schema import AIChatLogCreate, AIChatLogResponse, AIChatLogUpdate


router = APIRouter(prefix="/ai-chat-logs", tags=["AI chat logs"])


@router.post("/", response_model=AIChatLogResponse, status_code=status.HTTP_201_CREATED)
def create_ai_chat_log(payload: AIChatLogCreate, session: Session = Depends(get_session)):
    chat_log = AIChatLog.model_validate(payload)
    session.add(chat_log)
    try:
        session.commit()
        session.refresh(chat_log)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario o refrigerador indicado no existe") from error
    return chat_log


@router.get("/", response_model=list[AIChatLogResponse])
def get_ai_chat_logs(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(AIChatLog).offset(offset).limit(limit)).all()


@router.get("/{chat_log_id}", response_model=AIChatLogResponse)
def get_ai_chat_log(chat_log_id: int, session: Session = Depends(get_session)):
    chat_log = session.get(AIChatLog, chat_log_id)
    if chat_log is None:
        raise HTTPException(status_code=404, detail="Registro de chat no encontrado")
    return chat_log


@router.put("/{chat_log_id}", response_model=AIChatLogResponse)
def update_ai_chat_log(
    chat_log_id: int,
    payload: AIChatLogUpdate,
    session: Session = Depends(get_session),
):
    chat_log = session.get(AIChatLog, chat_log_id)
    if chat_log is None:
        raise HTTPException(status_code=404, detail="Registro de chat no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(chat_log, field, value)
    try:
        session.add(chat_log)
        session.commit()
        session.refresh(chat_log)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El usuario o refrigerador indicado no existe") from error
    return chat_log


@router.delete("/{chat_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_chat_log(chat_log_id: int, session: Session = Depends(get_session)):
    chat_log = session.get(AIChatLog, chat_log_id)
    if chat_log is None:
        raise HTTPException(status_code=404, detail="Registro de chat no encontrado")
    session.delete(chat_log)
    session.commit()