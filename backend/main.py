from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/search")
def search(q: str):
    q = (q or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query is required")

    url = "https://itunes.apple.com/search"
    params = {
        "term": q,
        "limit": 5,
        "media": "music",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Search provider error: {e}")

    results = []

    for item in data.get("results", []):
        preview = item.get("previewUrl")
        title = item.get("trackName")
        artist = item.get("artistName")

        if preview and title and artist:
            results.append(
                {
                    "title": title,
                    "artist": artist,
                    "preview_url": preview,
                }
            )

    return results
