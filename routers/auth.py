from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserLogin, Token
from utils.auth_utils import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"]
)

@router.post("/register/", response_model=UserResponse)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
    ):

    db_user = db.query(User).filter(User.username == user_in.username).first()

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач з таким юзернеймом вже існує"
        )
    
    user = User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
        is_active=True,
        role="user"
        )
    
    db.add(user)
    db.commit()

    db.refresh(user)

    return user

@router.post("/login/", response_model=Token)
def login_user(
    user_in: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == user_in.username).first()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,\
            detail="Неправильний логін або пароль спробуйте ще раз",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = {
        "sub": str(user.user_id),
        "username": user.username,
        "role": user.role
    }

    access_token = create_access_token(user_data)

    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

