import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TIKTOK_URL = "https://www.tiktok.com/@alexey_pv_/"

START_TEXT = (
    "🚀 <b>OTG Media Network</b>\n\n"
    "Музыка, клипы и персональные песни — в одном месте.\n\n"
    "🎵 Для музыки открой приложение через кнопку внизу чата.\n"
    "🎬 Эфир доступен по кнопке ниже."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Музыкальный эфир OTG в TikTok", url=TIKTOK_URL)],
    ])
    await update.message.reply_html(START_TEXT, reply_markup=keyboard)

def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
