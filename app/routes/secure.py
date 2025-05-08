# app/routes/secure.py

from fastapi import APIRouter, Depends, HTTPException, status
from app.security import get_current_user
from app.models import Student

router = APIRouter(prefix="/secure", tags=["Secure"])

# --------------------------------------------
# Route accessible to any authenticated user
# --------------------------------------------
@router.get("/me")
def get_my_profile(current_user: Student = Depends(get_current_user)):
    """
    Returns the profile of the currently authenticated user.
    """
    return {
        "email": current_user.email,
        "name": f"{current_user.first_name} {current_user.last_name}",
        "id": str(current_user.user_id),
        "role": current_user.role
    }


# --------------------------------------------------
# General protected route, for any authenticated user
# --------------------------------------------------
@router.get("")
def read_secure_data(current_user: Student = Depends(get_current_user)):
    """
    Basic protected route for authenticated users.
    """
    return {"message": f"Hello, {current_user.first_name}! You are authorized."}


# --------------------------------------------------
# Admin-only route
# --------------------------------------------------
@router.get("/admin")
def read_admin_data(current_user: Student = Depends(get_current_user)):
    """
    Admin-only route. Only users with role 'admin' can access.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return {"message": f"Welcome Admin {current_user.first_name}!"}


# --------------------------------------------------
# Student-only route
# --------------------------------------------------
@router.get("/student")
def read_student_data(current_user: Student = Depends(get_current_user)):
    """
    Student-only route. Only users with role 'student' can access.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Students only")
    return {"message": f"Welcome Student {current_user.first_name}!"}

