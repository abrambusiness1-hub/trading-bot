import telebot
from openai import OpenAI
import base64
import os

# TOKENS (Railway ENV)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

user_data = {}

# =====================
# 🔥 SNIPER PROMPT
# =====================
PROMPT = """You are an elite ICT (Inner Circle Trader) sniper.

You analyze TWO charts:
- First image = HTF (bias & liquidity)
- Second image = LTF (execution)

=====================
CORE LOGIC
=====================

Use EMA 50 & 200:
- Above = bullish
- Below = bearish

Liquidity:
- Highs = buy-side liquidity
- Lows = sell-side liquidity

MSS (Market Structure Shift):
- REQUIRED before entry
- Must show displacement (strong move)

FVG (Fair Value Gap):
- Use fresh imbalance
- Entry INSIDE FVG

Premium / Discount:
- Premium → prefer SELL
- Discount → prefer BUY

=====================
CRITICAL FIX (VERY IMPORTANT)
=====================

You are NOT trend locked.

You MUST consider BOTH:
1. Trend continuation trades
2. Counter-trend reversal trades

Counter-trend is ALLOWED IF:
- Strong liquidity sweep happens
- Clear MSS follows

=====================
ENTRY PRIORITY
=====================

1. Liquidity sweep (MANDATORY)
2. MSS confirmation
3. Return to FVG
4. EMA 50 confluence (preferred)

=====================
ENTRY RULES
=====================

BUY:
- Sell-side liquidity taken
- MSS UP
- Entry in discount/FVG

SELL:
- Buy-side liquidity taken
- MSS DOWN
- Entry in premium/FVG

=====================
EXECUTION
=====================

- NEVER chase
- WAIT for pullback
- Entry must be tight zone
- SL beyond liquidity
- TP at next liquidity

RR:
- Minimum 1:2

=====================
OUTPUT
=====================

Direction: BUY or SELL

WAIT FOR:
(clear condition)

Entry Zone:
(price range)

Stop Loss:
(price)

Take Profit:
(price)

⚠️ NEVER say "no trade"
"""

# =====================
# RESET COMMAND
# =====================
@bot.message_handler(commands=['reset'])
def reset(message):
    user_data[message.chat.id] = []
    bot.send_message(message.chat.id, "Reset yapıldı 🔄")

# =====================
# HANDLE PHOTOS
# =====================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id

    # foto indir
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    filename = f"{user_id}.jpg"
    with open(filename, "wb") as f:
        f.write(downloaded_file)

    # base64 çevir
    with open(filename, "rb") as img:
        b64 = base64.b64encode(img.read()).decode()

    if user_id not in user_data:
        user_data[user_id] = []

    user_data[user_id].append(b64)

    # 1. foto
    if len(user_data[user_id]) == 1:
        bot.send_message(user_id, "HTF geldi 👍 şimdi LTF at")
        return

    # 2. foto → analiz
    if len(user_data[user_id]) == 2:

        img1 = user_data[user_id][0]
        img2 = user_data[user_id][1]

        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": PROMPT
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{img1}"
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{img2}"
                        }
                    ]
                }]
            )

            bot.send_message(user_id, response.output_text)

        except Exception as e:
            bot.send_message(user_id, f"Hata: {e}")

        # reset
        user_data[user_id] = []

# =====================
# START BOT
# =====================
print("Bot çalışıyor 🚀")
bot.infinity_polling()