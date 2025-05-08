# app/routes/food.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schema, database
from app.database import get_db
from app.security import require_admin
import uuid

router = APIRouter(prefix="/food", tags=["Food"])

# -------------------------
# Create Food (Admin only)
# -------------------------
@router.post("/", response_model=schema.FoodOut)
def create_food(
    food: schema.FoodCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    new_food = models.Food(**food.model_dump())
    db.add(new_food)
    db.commit()
    db.refresh(new_food)
    return new_food


# -------------------------
# Get All Food (Public)
# -------------------------
@router.get("/", response_model=list[schema.FoodOut])
def get_all_food(db: Session = Depends(get_db)):
    return db.query(models.Food).all()


# -------------------------
# Get One Food (Public)
# -------------------------
@router.get("/{food_id}", response_model=schema.FoodOut)
def get_food(food_id: uuid.UUID, db: Session = Depends(get_db)):
    food = db.query(models.Food).filter(models.Food.food_id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return food


# -------------------------
# Update Food (Admin only)
# -------------------------
@router.put("/{food_id}", response_model=schema.FoodOut)
def update_food(
    food_id: uuid.UUID,
    update_data: schema.FoodCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    food = db.query(models.Food).filter(models.Food.food_id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    for key, value in update_data.dict().items():
        setattr(food, key, value)

    db.commit()
    db.refresh(food)
    return food


# -------------------------
# Delete Food (Admin only)
# -------------------------
@router.delete("/{food_id}")
def delete_food(
    food_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    food = db.query(models.Food).filter(models.Food.food_id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    db.delete(food)
    db.commit()
    return {"detail": "Food deleted"}


