from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.config import BOT_TOKEN
from bot.handlers import start, handle_message

async def main():
    """Run the Telegram bot."""
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running on Railway...")
    await app.run_polling()
