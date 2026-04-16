import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# kullanıcıya özel hafıza
user_images = {}

SYSTEM_PROMPT = """
You are a professional ICT trader.

You analyze TWO charts:
1st image = HTF
2nd image = LTF

Rules:
- Use EMA 50 & 200
- Identify liquidity
- Wait for sweep
- Confirm MSS
- Use FVG

Give ONE combined setup.

FORMAT:

Direction:
WAIT FOR:
Entry Zone:
Stop Loss:
Take Profit:

NO EXTRA TEXT
"""

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("HTF gönder kanka 👍")

# foto handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = f"{user_id}.jpg"
    await file.download_to_drive(file_path)

    # ilk foto
    if user_id not in user_images:
        user_images[user_id] = [file_path]
        await update.message.reply_text("HTF geldi 👍 şimdi LTF at")
        return

    # ikinci foto
    else:
        user_images[user_id].append(file_path)

        htf = user_images[user_id][0]
        ltf = user_images[user_id][1]

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze HTF and LTF charts"},
                        {"type": "image_url", "image_url": {"url": f"file://{htf}"}},
                        {"type": "image_url", "image_url": {"url": f"file://{ltf}"}}
                    ]
                }
            ]
        )

        result = response.choices[0].message.content
        await update.message.reply_text(result)

        # reset
        user_images[user_id] = []

# main
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot çalışıyor 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()