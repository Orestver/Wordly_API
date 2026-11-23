from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserUpdate, UserResponse
from utils.auth_utils import get_current_user, hash_password

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Отримати дані власного профілю"""
    return current_user

@router.put("/me")
def update_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):

    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        current_user.hashed_password = hash_password(update_data["password"])
        del update_data["password"]

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    
    return {"message": "Профіль успішно оновлено"}
