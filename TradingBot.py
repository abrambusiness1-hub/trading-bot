import os
import base64
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# 🔐 ENV
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# 🧠 ICT PROMPT
SYSTEM_PROMPT = """
You are a professional ICT (Inner Circle Trader) trader.

You think like smart money, not retail.

You analyze TWO charts:
- First image = HTF (1H or 4H)
- Second image = LTF (5m or 15m)

=====================
RULES
=====================

- Use EMA 50 & EMA 200 for trend bias
- Identify liquidity (BSL / SSL)
- Wait for liquidity sweep
- Confirm MSS (Market Structure Shift)
- Use FVG / IFVG as entry zones
- Use Premium / Discount

=====================
ENTRY MODEL
=====================

SELL:
- HTF bearish
- Sweep highs
- MSS down
- Return to FVG in premium

BUY:
- HTF bullish
- Sweep lows
- MSS up
- Return to FVG in discount

=====================
STRICT RULES
=====================

- NEVER say WAIT
- ALWAYS give a setup
- Entry must be zone
- SL beyond liquidity
- TP = next liquidity
- RR minimum 1:2

=====================
OUTPUT FORMAT
=====================

Direction: BUY or SELL

WAIT FOR:
(exact condition or level)

Entry Zone:
(price range)

Stop Loss:
(price)

Take Profit:
(price)

NO EXTRA TEXT
"""

# 🚀 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif kanka 🚀 Foto gönder")

# 📸 IMAGE HANDLER (FIXED)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = "chart.jpg"
    await file.download_to_drive(file_path)

    # 📸 base64'e çevir (ÖNEMLİ FIX)
    with open(file_path, "rb") as img:
        image_base64 = base64.b64encode(img.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this chart"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    )

    result = response.choices[0].message.content
    await update.message.reply_text(result)

# 🏁 MAIN
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot çalışıyor 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()