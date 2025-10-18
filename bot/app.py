from flask import Flask
import threading
from bot.main import main  # runs your Telegram bot

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Savvy Chatbot is running on Render!"

def run_bot():
    main()  # starts the Telegram bot (polling mode)

if __name__ == '__main__':
    # Run the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Bind to the Render port
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
from flask import Flask
import threading
from bot.main import main  # runs your Telegram bot

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Savvy Chatbot is running on Render!"

def run_bot():
    main()  # starts the Telegram bot (polling mode)

if __name__ == '__main__':
    # Run the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Bind to the Render port
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
