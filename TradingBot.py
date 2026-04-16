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

FORMAT STRICT:

Direction:
WAIT FOR:
Entry Zone:
Stop Loss:
Take Profit:

NO EXTRA TEXT
"""

# START (artık reset yapmaz)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("HTF gönder kanka 👍")

# RESET 🔥
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_images[user_id] = []
    await update.message.reply_text("Reset yapıldı 🔄 yeniden HTF at")

# FOTO
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_url = file.file_path

    # ilk foto
    if user_id not in user_images or len(user_images[user_id]) == 0:
        user_images[user_id] = [file_url]
        await update.message.reply_text("HTF geldi 👍 şimdi LTF at")
        return

    # ikinci foto
    elif len(user_images[user_id]) == 1:
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

        # reset otomatik
        user_images[user_id] = []

# MAIN
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))  # 🔥 EKLENDİ
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot çalışıyor 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()