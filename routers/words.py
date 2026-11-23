
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Dictionary, User, Word
from schemas import WordBatchCreate, WordCreate, WordResponse, WordUpdate
from utils.auth_utils import get_current_user

router = APIRouter(tags=["Words"])

@router.get("/api/v1/dictionaries/{dict_id}/words", response_model=list[WordResponse])
def get_words(
    dict_id: int,
    db: Session = Depends(get_db)
    ):

    words = db.query(Word).filter(Word.dict_id == dict_id).all()

    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У цьому словнику немає слів"
        )

    return words

@router.post("/api/v1/dictionaries/{dict_id}/words", response_model=WordResponse)
def add_word(
    dict_id: int,
    word_in: WordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):

    db_dictionary = db.query(Dictionary).filter(Dictionary.dict_id == dict_id).first()

    if not db_dictionary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Словник з ID {dict_id} не знайдено. Спочатку створіть його."
        )

    word = Word(
        original_word = word_in.original_word,
        translation = word_in.translation,
        dict_id = dict_id
    )

    db.add(word)
    db.commit()

    db.refresh(word)
    
    return word

@router.post("/api/v1/dictionaries/{dict_id}/words/batch")
def add_words_batch(
    dict_id: int,
    batch_data: WordBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    dictionary = db.query(Dictionary).filter(
        Dictionary.dict_id == dict_id,
        Dictionary.user_id == current_user.user_id
    ).first()

    if not dictionary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Словник не знайдено або він вам не належить"
        )

    new_words = []
    for item in batch_data.words:
        word = Word(
            original_word = item.original_word,
            translation = item.translation,
            dict_id = dict_id
        )

        new_words.append(word)

    db.add_all(new_words)
    db.commit()

    return {
        "message": f"Успішно додано {len(new_words)} слів",
        "added_count": len(new_words)
    }

@router.put("/api/v1/words/{word_id}", response_model=WordResponse)
def update_word(
    dict_id: int,
    word_id: int,
    word_in: WordUpdate,
    db: Session = Depends(get_db),
    ):

    word = db.query(Word).filter(Word.dict_id == dict_id,
                                 Word.word_id == word_id
                                 ).first()

    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not fount"
        )

    if word_in.original_word is not None:
        word.original_word = word_in.original_word

    if word_in.translation is not None:
        word.translation = word_in.translation

    db.commit()
    db.refresh(word)

    return word

@router.delete("/api/v1/words/{word_id}")
def delete_word(
    dict_id: int,
    word_id: int,
    db: Session = Depends(get_db),
    ) -> None:

    word = db.query(Word).filter(Word.dict_id == dict_id, 
                                 Word.word_id == word_id
                                 ).first()

    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not fount"
        )

    db.delete(word)
    db.commit()

