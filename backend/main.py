from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

origins = [
    "https://otg-mini-app-clean-production.up.railway.app",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def search(q: str):
    url = f"https://api.deezer.com/search?q={q}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()

    result = []
    for item in data.get("data", []):
        result.append({
            "title": item.get("title"),
            "artist": item.get("artist", {}).get("name"),
            "preview_url": item.get("preview"),
        })

    return result
