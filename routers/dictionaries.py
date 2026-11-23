from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Dictionary, User
from schemas import DictionaryCreate, DictionaryResponse, DictionaryUpdate
from utils.auth_utils import get_current_user

router = APIRouter(
    prefix="/api/v1/dictionaries",
    tags=["Dictionaries"]
)

@router.get("/", response_model=List[DictionaryResponse])
def get_dictionaries(  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), 
    ):
    dictionaries = db.query(Dictionary).filter(Dictionary.user_id == current_user.user_id).all()
    if not dictionaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У йцього користувача покищо немає словників"
        )
    return dictionaries

@router.get("/{dict_id}/", response_model=DictionaryResponse)
def get_dictionary_by_id(
    dict_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  
    ):
    dictionary = db.query(Dictionary).filter(Dictionary.user_id == current_user.user_id,
                                             Dictionary.dict_id == dict_id
                                             ).first()
    if not dictionary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Словник не знайдено"
        )
    return dictionary

@router.post("/", response_model=DictionaryResponse)
def create_dictionary(
    dictionary_in: DictionaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):

    db_user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з ID {current_user.user_id} не знайдено. Спочатку зареєструйте його."
        )
    
    dictionary = Dictionary(
        title = dictionary_in.title,
        description = dictionary_in.description,
        user_id = current_user.user_id
    )

    db.add(dictionary)
    db.commit()

    db.refresh(dictionary)
    
    return dictionary

@router.put("/{dict_id}", response_model=DictionaryResponse)
def update_dictionary(
    dict_id: int,
    dictionary_in: DictionaryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dictionary = db.query(Dictionary).filter(Dictionary.user_id == current_user.user_id,
                                             Dictionary.dict_id == dict_id
                                             ).first()

    if not dictionary:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Словник не знайдено"
        )
    
    if dictionary_in.title is not None:
        dictionary.title = dictionary_in.title

    if dictionary_in.description is not None:
        dictionary.description = dictionary_in.description

    db.commit()
    db.refresh(dictionary)

    return dictionary

@router.delete("/{dict_id}/")
def delete_dictionary(
    dict_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), 
):
    dictionary = db.query(Dictionary).filter(Dictionary.user_id == current_user.user_id,
                                             Dictionary.dict_id == dict_id
                                             ).first()

    if not dictionary:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Словник не знайдено"
        )
    
    db.delete(dictionary)
    db.commit()

    return None
