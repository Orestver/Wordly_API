from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False) 
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")             
    is_active = Column(Boolean, default=True, nullable=False)             
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Зв'язок: один користувач має багато словників
    dictionaries = relationship("Dictionary", back_populates="owner",
                            cascade="all, delete", passive_deletes=True)

class Dictionary(Base):
    __tablename__ = "dictionaries"

    dict_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Зв'язок із користувачем та словами
    owner = relationship("User", back_populates="dictionaries")
    words = relationship("Word", back_populates="dictionary",
                     cascade="all, delete", passive_deletes=True)

class Word(Base):
    __tablename__ = "words"

    word_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dict_id = Column(Integer, ForeignKey("dictionaries.dict_id", ondelete="CASCADE"), nullable=False)
    original_word = Column(String(100), nullable=False)
    translation = Column(String(100), nullable=False)
    is_learned = Column(Boolean, default=False)

    # Зв'язок зі словником
    dictionary = relationship("Dictionary", back_populates="words")