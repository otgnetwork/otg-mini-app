from fastapi import FastAPI, HTTPException, Query
from deezer import search_track

app = FastAPI(title="Music Bot Backend")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/search")
async def search(q: str = Query(..., min_length=1)) -> dict:
    try:
        return await search_track(q)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
