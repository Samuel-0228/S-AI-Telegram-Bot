import asyncio
import threading
from flask import Flask
from bot.main import main  # Import your Telegram bot's main() function

app = Flask(__name__)

def run_bot():
    """Run the Telegram bot in its own asyncio event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

# Run the Telegram bot in a separate thread
threading.Thread(target=run_bot, daemon=True).start()

@app.route("/")
def home():
    return "🤖 Savvy AAU Telegram Bot is running successfully on Railway!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
