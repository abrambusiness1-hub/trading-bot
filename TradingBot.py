import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

user_images = {}

SYSTEM_PROMPT = """
You are a professional ICT trader.

Analyze HTF and LTF together.

Rules:
- EMA 50 & 200
- Liquidity sweep
- MSS
- FVG
- Premium / Discount

ALWAYS give full setup.

FORMAT STRICT:

Direction:
WAIT FOR:
Entry Zone:
Stop Loss:
Take Profit:

DO NOT SKIP ANY FIELD
DO NOT WRITE EXTRA TEXT
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("HTF gönder kanka 👍")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_url = file.file_path

    if user_id not in user_images:
        user_images[user_id] = [file_url]
        await update.message.reply_text("HTF geldi 👍 şimdi LTF at")
        return

    else:
        user_images[user_id].append(file_url)

        htf = user_images[user_id][0]
        ltf = user_images[user_id][1]

        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Analyze both charts"},
                        {"type": "input_image", "image_url": htf},
                        {"type": "input_image", "image_url": ltf}
                    ]
                }
            ]
        )

        result = response.output_text

        await update.message.reply_text(result)

        user_images[user_id] = []

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot çalışıyor 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()