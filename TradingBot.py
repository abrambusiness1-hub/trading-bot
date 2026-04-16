import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# 🔥 SNIPER PROMPT (FIXED)
SYSTEM_PROMPT = """You are an elite ICT sniper trader with a focus on high win-rate setups (70–80% accuracy).

You will receive TWO chart images in ONE message.

AUTO DETECT:
- The chart with larger timeframe structure (cleaner, slower candles) = HTF
- The chart with more candles / faster movement = LTF

=====================
CORE SYSTEM (HIGH WINRATE MODE)
=====================

You ONLY take A+ setups.

A+ setup MUST include:
1. Clear HTF bias
2. Liquidity sweep (NOT optional)
3. Clean MSS (strong displacement)
4. Entry at FVG with confluence
5. EMA alignment (50 & 200)

If any of these are weak → still give setup BUT:
→ make WAIT FOR stricter (more confirmation)

=====================
HTF ANALYSIS
=====================

- Identify trend using EMA 50 & EMA 200
- Mark key liquidity:
  - Previous highs/lows
  - Equal highs/lows
- Determine draw on liquidity (target)

- Define zones:
  - Premium → SELL only
  - Discount → BUY only

=====================
LTF EXECUTION
=====================

You MUST follow this order:

1. Liquidity Sweep
2. MSS (strong displacement)
3. FVG entry
4. Pullback (NO chasing)

=====================
ENTRY RULES
=====================

BUY:
- HTF bullish
- Sweep lows
- MSS up
- Entry in discount FVG

SELL:
- HTF bearish
- Sweep highs
- MSS down
- Entry in premium FVG

=====================
FILTER
=====================

- Avoid sideways
- Avoid weak MSS
- Avoid mid-range

If unclear → give stricter WAIT FOR

=====================
OUTPUT
=====================

Direction: BUY or SELL

WAIT FOR:
- liquidity level
- MSS confirmation
- return to FVG

Entry Zone:
- tight range

Stop Loss:
- beyond liquidity

Take Profit:
- HTF liquidity

RR:
- 1:2 or higher

NO explanation.
"""

# 📸 MEDIA GROUP MEMORY
media_groups = {}

async def handle_album(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    media_group_id = message.media_group_id

    # ❗ Eğer tek foto gönderirse
    if not media_group_id:
        await update.message.reply_text("2 fotoyu aynı anda gönder kanka 📸")
        return

    # grup başlat
    if media_group_id not in media_groups:
        media_groups[media_group_id] = []

    photo = message.photo[-1]
    file = await photo.get_file()
    file_url = file.file_path

    media_groups[media_group_id].append(file_url)

    # 2 foto bekle
    if len(media_groups[media_group_id]) < 2:
        return

    images = media_groups[media_group_id]
    img1 = images[0]
    img2 = images[1]

    # temizle
    del media_groups[media_group_id]

    # 🔥 AI ANALİZ
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
                    {"type": "input_image", "image_url": img1},
                    {"type": "input_image", "image_url": img2}
                ]
            }
        ]
    )

    result = response.output_text

    await update.message.reply_text(result)

# 🚀 MAIN
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.PHOTO, handle_album))

    print("Bot çalışıyor 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()