from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schema, database
from app.database import get_db
from app.security import require_admin
import uuid

router = APIRouter(prefix="/suggestions", tags=["Suggestions"])

# -------------------------------
# Create a Food Suggestion (Admin only)
# -------------------------------
@router.post("/", response_model=schema.SuggestionOut)
def create_suggestion(
    food_suggestion: schema.SuggestionCreate,
    db: Session = Depends(database.get_db),
    current_user=Depends(require_admin)
):
    new_suggestion = models.Suggestion(**food_suggestion.model_dump())
    db.add(new_suggestion)
    db.commit()
    db.refresh(new_suggestion)
    return new_suggestion


# -------------------------------
# Get all Food Suggestions (Public)
# -------------------------------
@router.get("/", response_model=list[schema.SuggestionOut])
def get_all_suggestion(db: Session = Depends(get_db)):
    return db.query(models.Suggestion).all()


# -------------------------------
# Get one Food Suggestion (Public)
# -------------------------------
@router.get("/{suggestion_id}", response_model=schema.SuggestionOut)
def get_suggestion(suggestion_id: uuid.UUID, db: Session = Depends(get_db)):
    food_suggestion = db.query(models.Suggestion).filter(models.Suggestion.suggestion_id == suggestion_id).first()
    if not food_suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return food_suggestion


# -------------------------------
# Update Food Suggestion (Admin only)
# -------------------------------
@router.put("/{suggestion_id}", response_model=schema.SuggestionOut)
def update_suggestion(
    suggestion_id: uuid.UUID,
    update_data: schema.SuggestionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    food_suggestion = db.query(models.Suggestion).filter(models.Suggestion.suggestion_id == suggestion_id).first()
    if not food_suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    for key, value in update_data.dict().items():
        setattr(food_suggestion, key, value)

    db.commit()
    db.refresh(food_suggestion)
    return food_suggestion


# -------------------------------
# Delete Food Suggestion (Admin only)
# -------------------------------
@router.delete("/{suggestion_id}")
def delete_suggestion(
    suggestion_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    food_suggestion = db.query(models.Suggestion).filter(models.Suggestion.suggestion_id == suggestion_id).first()
    if not food_suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    db.delete(food_suggestion)
    db.commit()
    return {"detail": "Suggestion deleted"}


