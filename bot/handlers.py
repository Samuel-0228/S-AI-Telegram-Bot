import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from .ai import generate_reply


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply to /start command."""
    await update.message.reply_text(
        "🤖 Hello! I’m Savvy Chatbot — your AAU AI assistant built by Savvy Society Coordinator.\n"
        "🌐 Channel: https://t.me/Savvy_Society\n\n"
        "Send me any question about Addis Ababa University or general topics!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply to user messages using AI, with a quick 'working...' message."""
    user_text = (update.message.text or "").strip()

    if not user_text:
        await update.message.reply_text("Please send a text message.")
        return

    # let the user know we're processing
    working_msg = await update.message.reply_text("💭 Working on it...")

    # run generate_reply in a background thread to avoid blocking
    ai_response = await asyncio.to_thread(generate_reply, user_text)

    # try to edit placeholder; if fails, send as new message
    try:
        await working_msg.edit_text(ai_response)
    except Exception:
        await update.message.reply_text(ai_response)
