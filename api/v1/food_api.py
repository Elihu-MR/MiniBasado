from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.common import utc_now
from models.food_model import Food
from schemas.food_schema import FoodCreate, FoodResponse, FoodUpdate


router = APIRouter(prefix="/foods", tags=["Foods"])


@router.post("/", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
def create_food(payload: FoodCreate, session: Session = Depends(get_session)):
    food = Food.model_validate(payload)
    session.add(food)
    try:
        session.commit()
        session.refresh(food)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El refrigerador indicado no existe") from error
    return food


@router.get("/", response_model=list[FoodResponse])
def get_foods(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(Food).offset(offset).limit(limit)).all()


@router.get("/{food_id}", response_model=FoodResponse)
def get_food(food_id: int, session: Session = Depends(get_session)):
    food = session.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Alimento no encontrado")
    return food


@router.put("/{food_id}", response_model=FoodResponse)
def update_food(food_id: int, payload: FoodUpdate, session: Session = Depends(get_session)):
    food = session.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Alimento no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(food, field, value)
    food.updated_at = utc_now()
    try:
        session.add(food)
        session.commit()
        session.refresh(food)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El refrigerador indicado no existe") from error
    return food


@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food(food_id: int, session: Session = Depends(get_session)):
    food = session.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Alimento no encontrado")
    try:
        session.delete(food)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar: hay imágenes relacionadas") from error