import os
import asyncio
import urllib.request

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder

import yt_dlp

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAIN_BOT_URL = "https://t.me/otgmusicbot"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

user_mode: dict[int, str] = {}


def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎬 Найти клип", callback_data="menu:clips")
    builder.button(text="🔥 Популярные клипы", callback_data="menu:popular")
    builder.button(text="✨ Заказать песню", url=MAIN_BOT_URL)
    builder.adjust(1)
    return builder.as_markup()


def clip_result_keyboard(url: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ Смотреть", url=url)
    builder.adjust(1)
    return builder.as_markup()


async def search_youtube_clips(query: str, limit: int = 3) -> list[dict]:
    def _search():
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "force_generic_extractor": False,
        }

        search_query = f"ytsearch{limit}:{query} official music video"
        results = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)

        entries = info.get("entries", []) if info else []

        for entry in entries:
            video_id = entry.get("id")
            title = entry.get("title") or "Unknown title"
            channel = entry.get("channel") or entry.get("uploader") or "Unknown channel"
            thumbnail = entry.get("thumbnail")

            if not video_id:
                continue

            if not thumbnail:
                thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

            results.append(
                {
                    "title": title,
                    "channel": channel,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": thumbnail,
                }
            )

        return results

    return await asyncio.to_thread(_search)


async def download_image(url: str):
    if not url:
        return None

    def _download():
        with urllib.request.urlopen(url, timeout=20) as response:
            return response.read()

    try:
        return await asyncio.to_thread(_download)
    except Exception:
        return None


async def send_clip_results(message: Message, query: str) -> None:
    await message.answer("🔎 Ищу клипы...")

    try:
        clips = await search_youtube_clips(query, limit=3)

        if not clips:
            await message.answer(
                "😔 Ничего не найдено.\n\n"
                "Попробуй другое название трека или артиста.",
                reply_markup=main_menu()
            )
            return

        for clip in clips:
            caption = (
                f"🎬 <b>{clip['title']}</b>\n\n"
                f"👤 {clip['channel']}\n\n"
                f"Смотри клип 👇"
            )

            image_bytes = await download_image(clip.get("thumbnail"))

            if image_bytes:
                await message.answer_photo(
                    photo=BufferedInputFile(image_bytes, filename="thumbnail.jpg"),
                    caption=caption,
                    reply_markup=clip_result_keyboard(clip["url"])
                )
            else:
                await message.answer(
                    caption,
                    reply_markup=clip_result_keyboard(clip["url"])
                )

        await message.answer(
            "👇 Выбери действие:",
            reply_markup=main_menu()
        )

    except Exception as e:
        print("CLIP SEARCH ERROR:", e)
        await message.answer(
            "❌ Ошибка поиска клипов. Попробуй позже.",
            reply_markup=main_menu()
        )


@dp.message(CommandStart())
async def start(message: Message):
    user_mode[message.from_user.id] = "clips"

    await message.answer(
        "🎬 <b>OTG Clips</b>\n\n"
        "Я помогу найти музыкальные клипы 🔥\n\n"
        "Просто напиши название трека или исполнителя\n"
        "или выбери действие ниже 👇",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "menu:clips")
async def menu_clips(callback: CallbackQuery):
    user_mode[callback.from_user.id] = "clips"

    await callback.message.answer(
        "🎬 <b>Поиск клипов</b>\n\n"
        "Отправь название трека или исполнителя.\n"
        "Пример: <code>Eminem</code>"
    )
    await callback.answer()


@dp.callback_query(F.data == "menu:popular")
async def menu_popular(callback: CallbackQuery):
    user_mode[callback.from_user.id] = "clips"

    await callback.message.answer(
        "🔥 <b>Популярные запросы</b>\n\n"
        "Попробуй написать:\n"
        "— Eminem\n"
        "— The Weeknd\n"
        "— Rihanna\n"
        "— Drake\n"
        "— Billie Eilish"
    )
    await callback.answer()


@dp.message()
async def handle_text(message: Message):
    text = (message.text or "").strip()

    if not text:
        await message.answer("Отправь текстовый запрос.")
        return

    user_mode[message.from_user.id] = "clips"
    await send_clip_results(message, text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
