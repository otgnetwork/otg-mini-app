from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def search(q: str):
    url = f"https://api.deezer.com/search?q={q}"
    r = requests.get(url)
    data = r.json()

    result = []
    for item in data.get("data", []):
        result.append({
            "title": item["title"],
            "artist": item["artist"]["name"],
            "preview_url": item["preview"]
        })

    return result
