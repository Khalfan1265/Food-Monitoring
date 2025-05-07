from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.models import Student  # SQLAlchemy model
from app.schema import LoginRequest, TokenResponse, PasswordResetConfirm  # Pydantic schemas
from app.security import verify_password, create_access_token, verify_reset_token, hash_password
from app.database import get_db

router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# -------------------------------
# Login endpoint
# -------------------------------
@router.post("/auth/login", response_model=TokenResponse)
def login_student(login: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return a JWT access token.
    """
    # Find student by email
    student = db.query(Student).filter(Student.email == login.email).first()
    
    # Validate credentials
    if not student or not verify_password(login.password, student.user_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    # Create token with email and role
    token = create_access_token(data={"sub": student.email, "role": student.role})
    
    # Return token
    return {"access_token": token}


@router.post("/auth/reset-confirm")
def confirm_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    email = verify_reset_token(data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="User not found")

    student.user_password = hash_password(data.new_password)
    db.commit()
    return {"detail": "Password reset successful"}


