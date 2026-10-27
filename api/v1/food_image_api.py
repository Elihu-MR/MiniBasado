from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db.database import get_session
from models.food_image_model import FoodImage
from schemas.food_image_schema import FoodImageCreate, FoodImageResponse, FoodImageUpdate


router = APIRouter(prefix="/food-images", tags=["Food images"])


@router.post("/", response_model=FoodImageResponse, status_code=status.HTTP_201_CREATED)
def create_food_image(payload: FoodImageCreate, session: Session = Depends(get_session)):
    food_image = FoodImage.model_validate(payload)
    session.add(food_image)
    try:
        session.commit()
        session.refresh(food_image)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El alimento o ticket indicado no existe") from error
    return food_image


@router.get("/", response_model=list[FoodImageResponse])
def get_food_images(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
):
    return session.exec(select(FoodImage).offset(offset).limit(limit)).all()


@router.get("/{food_image_id}", response_model=FoodImageResponse)
def get_food_image(food_image_id: int, session: Session = Depends(get_session)):
    food_image = session.get(FoodImage, food_image_id)
    if food_image is None:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return food_image


@router.put("/{food_image_id}", response_model=FoodImageResponse)
def update_food_image(
    food_image_id: int,
    payload: FoodImageUpdate,
    session: Session = Depends(get_session),
):
    food_image = session.get(FoodImage, food_image_id)
    if food_image is None:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(food_image, field, value)
    try:
        session.add(food_image)
        session.commit()
        session.refresh(food_image)
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(status_code=400, detail="El alimento o ticket indicado no existe") from error
    return food_image


@router.delete("/{food_image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_image(food_image_id: int, session: Session = Depends(get_session)):
    food_image = session.get(FoodImage, food_image_id)
    if food_image is None:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    session.delete(food_image)
    session.commit()