from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from deezer import search_tracks

app = FastAPI()

# 🔥 ВАЖНО: разрешаем запросы с фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно потом ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def search(q: str):
    return search_tracks(q)
