from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models import User, Dictionary
from schemas import UserCreate, AdminUserUpdate, UserOut
from utils.auth_utils import get_current_admin_user, hash_password

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin Panel"]
)

def _username_taken(db: Session, username: str, exclude_user_id: Optional[int] = None) -> bool:
    query = db.query(User).filter(func.lower(User.username) == username.lower())
    if exclude_user_id is not None:
        query = query.filter(User.user_id != exclude_user_id)
    return query.first() is not None

def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача з таким id незнайдено"
        )
    return user

# ---------------- Admin users operations -------------------

@router.get("/users", response_model=List[UserOut])
def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    return db.query(User).order_by(User.user_id).all()


@router.post("/users", response_model=UserOut)
def add_new_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    if _username_taken(db, user_in.username):
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


@router.post("/admin-users", response_model=UserOut)
def add_new_admin_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    if _username_taken(db, user_in.username):
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
    user = _get_user_or_404(db, user_id)

    update_data = user_update.model_dump(exclude_unset=True)

    if current_user.user_id == user_id and (
        "role" in update_data or "is_active" in update_data
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ви не можете змінити власну роль чи статус"
        )

    new_username = update_data.get("username")
    if new_username and _username_taken(db, new_username, exclude_user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач з таким юзернеймом вже існує"
        )

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
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ви не можете видалити власний обліковий запис"
        )

    user = _get_user_or_404(db, user_id)

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

    user = _get_user_or_404(db, user_id)

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

    dictionaries = (
        db.query(Dictionary)
        .filter(Dictionary.user_id == user_id)
        .order_by(Dictionary.dict_id)
        .all()
    )

    if not dictionaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У користувача немає створених словників"
        )

    return [
        {
            "dict_id": d.dict_id,
            "user_id": d.user_id,
            "title": d.title,
            "description": d.description,
            "created_at": d.created_at,
        }
        for d in dictionaries
    ]


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

    dictionaries = (
        db.query(Dictionary)
        .filter(Dictionary.user_id == user_id)
        .order_by(Dictionary.dict_id)
        .all()
    )

    if not dictionaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У користувача немає створених словників"
        )

    result = []
    for d in dictionaries:
        words = [
            {
                "word_id": w.word_id,
                "dict_id": w.dict_id,
                "original_word": w.original_word,
                "translation": w.translation,
                "is_learned": w.is_learned,
            }
            for w in sorted(d.words, key=lambda w: w.word_id)
        ]
        result.append({d.title: words})

    return result