from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Dictionary, Word
from schemas import UserCreate, AdminUserUpdate
from utils.auth_utils import get_current_admin_user, hash_password

router = APIRouter(
    prefix="/api/v1/admin", 
    tags=["Admin Panel"]
)

# ---------------- Admin users operations -------------------

@router.get("/users")
def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
    ):

    users = db.query(User).all()

    return users

@router.post("/users")
def add_new_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
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

@router.post("/admin-users")
def add_new_admin_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
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
        role="admin"
    )
    db.add(user)
    db.commit()

    db.refresh(user)

    return user

@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    ):

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача з таким id незнайдено"
        )

    update_data = user_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "password":
            user.hashed_password = hash_password(value)
        else:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return {"message": "Користувача успішно оновлено"}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    ):

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача з таким id незнайдено"
        )

    db.delete(user)
    db.commit()

    return None

@router.patch("/users/{user_id}/ban", status_code=status.HTTP_200_OK)
def ban_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ви не можете заблокувати власний обліковий запис"
        )

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача з таким ID не знайдено"
        )

    user.is_active = False

    db.commit()
    db.refresh(user)

    return {"message": f"Користувача '{user.username}' успішно заблоковано"}


# ---------------- Admin dictionaries operations -------------------

@router.get("/dictionaries/{user_id}")
def get_all_user_dictionaries(
    user_id: int, 
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
    ):

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з таким ID({user_id}) неіснує"
        )


    dictionaries = db.query(Dictionary).filter(Dictionary.user_id == user_id).all()

    if not dictionaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"У користувача немає створених словників"
        )
    
    return dictionaries


@router.get("/dictionaries/words/{user_id}")
def get_all_user_words(
    user_id: int, 
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
    ):

    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з таким ID({user_id}) неіснує"
        )


    dictionaries = db.query(Dictionary).filter(Dictionary.user_id == user_id).all()

    if not dictionaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"У користувача немає створених словників"
        )

    words = []

    for dict in dictionaries:
        words.append({dict.title: dict.words})

    return words
