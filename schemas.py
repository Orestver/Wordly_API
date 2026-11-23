from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, computed_field
# ===================== Users ============================

class UserCreate(BaseModel):
    username: str = Field(..., max_length=50, description="Юзернейм")
    password: str = Field(..., min_length=6,  max_length=255, description="Пароль")

class UserResponse(BaseModel):
    user_id: int
    username: str
    role: str
    is_active: bool
    model_config = {"from_attributes": True}

    @computed_field
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

class UserOut(BaseModel):
    user_id: int
    username: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    username: str | None = Field(None, max_length=50, description="Новий юзернейм")
    password: str | None = Field(None, min_length=6, max_length=255, description="Новий пароль")
    
class AdminUserUpdate(BaseModel):
    username: str | None = Field(None, max_length=50, description="Юзернейм")
    password: str | None = Field(None, min_length=6, max_length=255, description="Новий пароль")
    role: Literal["user", "admin"] | None = Field(None, description="Роль користувача")
    is_active: bool | None = Field(None, description="Чи активний користувач")

class UserLogin(BaseModel):
    username: str
    password: str 

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ===================== Dictionaries ======================

class DictionaryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=50, description="Назва словника")
    description: str | None = Field(None, max_length=255, description="Опис словника")

class DictionaryResponse(BaseModel):
    dict_id: int
    title: str = Field(..., min_length=1, max_length=50, description="Назва словника")
    description: str | None = Field(None, max_length=255, description="Опис словника")
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class DictionaryUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=50, description="Нова назва")
    description: str | None = Field(None, max_length=255, description="Новий опис")

# =======================  Words  ========================

class WordCreate(BaseModel):
    original_word: str = Field(..., max_length=100, description="Оригінальне слово")
    translation: str = Field(..., max_length=100, description="Переклад")

class WordBatchCreate(BaseModel):
    words: list[WordCreate] = Field(..., description="Список слів для додавання")
    
class WordResponse(BaseModel):
    word_id: int
    original_word: str = Field(..., max_length=100, description="Оригінальне слово")
    translation: str = Field(..., max_length=100, description="Переклад")
    dict_id: int
    is_learned: bool

    model_config = ConfigDict(from_attributes=True)

class WordUpdate(BaseModel):
    original_word: str | None = Field(None, max_length=100)
    translation: str | None = Field(None, max_length=100)
    is_learned: bool | None = None

class WordBatchUpdate(BaseModel):
    words: list[WordUpdate] = Field(..., description="Список слів для оновлення")


# =======================  Quizes  ========================

class QuizResult(BaseModel):
    correct_words_ids: list[int] = []
    incorrect_words_ids: list[int] = []