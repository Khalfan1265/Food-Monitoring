# app/routes/device.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schema, database
from app.database import get_db
from app.security import require_admin, get_current_user
import uuid

router = APIRouter(prefix="/device", tags=["Device"])


# -------------------------
# Create Device (Admin only)
# -------------------------
@router.post("/", response_model=schema.DeviceOut)
def create_device(
    device: schema.DeviceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    new_device = models.Device(**device.model_dump())
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device


# -------------------------
# Get All Devices (Public)
# -------------------------
@router.get("/", response_model=list[schema.DeviceOut])
def get_all_devices(db: Session = Depends(get_db)):
    return db.query(models.Device).all()


# -------------------------
# Get One Device (Public)
# -------------------------
@router.get("/{device_id}", response_model=schema.DeviceOut)
def get_device(device_id: uuid.UUID, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


# -------------------------
# Update Device (Admin only)
# -------------------------
@router.put("/{device_id}", response_model=schema.DeviceOut)
def update_device(
    device_id: uuid.UUID,
    update_data: schema.DeviceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    for key, value in update_data.dict().items():
        setattr(device, key, value)

    db.commit()
    db.refresh(device)
    return device


# -------------------------
# Delete Device (Admin only)
# -------------------------
@router.delete("/{device_id}")
def delete_device(
    device_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    db.delete(device)
    db.commit()
    return {"detail": "Device deleted"}
