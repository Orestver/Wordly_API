from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import admin, auth, dictionaries, quiz, users, words

# Цей рядок створює всі таблиці в базі даних на основі ваших класів у models.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(dictionaries.router)
app.include_router(words.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(quiz.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}