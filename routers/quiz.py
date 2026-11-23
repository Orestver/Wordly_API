import random
from typing import List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Dictionary, Word
from schemas import QuizResult
from utils.auth_utils import get_current_user
from utils.quiz_utils import get_options


router = APIRouter(prefix="/api/v1/dictionaries/{dict_id}",
                   tags=["Quiz"])

@router.get("/quiz")
def get_words_for_quiz(
    dict_id: int,
    mode: Literal["all", "count", "match", "mistakes"],
    limit: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):

    dictionary = db.query(Dictionary).filter(
        Dictionary.dict_id == dict_id,
        Dictionary.user_id == current_user.user_id
    ).first()

    if not dictionary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Словник не знайдено або у вас немає до нього доступу"
        )

    words = db.query(Word).filter(Word.dict_id == dict_id).all()

    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У цьому словнику немає слів"
        )

    random.shuffle(words)

    selected_words = []
    if mode == "all":
        selected_words = words

    if mode == "count":
        if not limit or limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Додайте кількість слів для тестування"
            )
        selected_words = words[:limit]

    if mode == "match":
        if len(words) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Додайте кількість слів для тестування"
            )
        selected_words = words

        result = []
        for word in selected_words:
            is_reversed = random.choice([False, True])
            result.append({
                "word_id": word.word_id,
                "original_word": word.original_word,
                "translation": word.translation,
                "options": get_options(selected_words, word, is_reversed),
                "reversed": is_reversed
            })
            
        return result

    if mode == "mistakes":
        selected_words = db.query(Word).filter(
            Word.dict_id == dict_id,
            Word.is_learned == False
        ).all()

    return [
        {
            "word_id": word.word_id,
            "original_word": word.original_word,
            "translation": word.translation,
            "reversed": random.choice([False, True])
        }
        for word in selected_words
    ]

@router.post("/quiz/results")
def save_quiz_results(
    dict_id: int,
    results: QuizResult,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):

    dictionary = db.query(Dictionary).filter(Dictionary.dict_id == dict_id,
                                             Dictionary.user_id == current_user.user_id).first()
    if not dictionary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Словник не знайдено або у вас немає до нього доступу"
        )

    if results.correct_words_ids:
        db.query(Word).filter(
            Word.dict_id == dict_id,
            Word.word_id.in_(results.correct_words_ids)
        ).update({"is_learned": True}, synchronize_session=False)

    # Повертаємо у невивчені ті, де були помилки
    if results.incorrect_words_ids:
        db.query(Word).filter(
            Word.dict_id == dict_id,
            Word.word_id.in_(results.incorrect_words_ids)
        ).update({"is_learned": False}, synchronize_session=False)

    db.commit()

    return {"message": "Результат збережено успішно"}

    




