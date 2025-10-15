from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from .config import BOT_TOKEN
from .handlers import start, handle_message


def main():
    # Create the bot application
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # Command handler for /start
    app.add_handler(CommandHandler("start", start))

    # Message handler for all other text messages
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running locally...")
    app.run_polling()


if __name__ == "__main__":
    main()
