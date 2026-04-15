import ssl
import certifi
import aiohttp


async def search_track(query: str) -> dict:
    url = "https://api.deezer.com/search"
    params = {"q": query}

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url, params=params, timeout=15) as response:
            response.raise_for_status()
            data = await response.json()

    return {
        "query": query,
        "results": data.get("data", [])
    }
