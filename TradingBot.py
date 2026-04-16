import telebot
from openai import OpenAI
import base64
import os

# 🔑 ENV (Railway)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

user_data = {}

# 🔥 SNIPER PROMPT (FIXED)
PROMPT = """You are an ICT sniper trader.

You analyze TWO charts:
- First = HTF
- Second = LTF

=====================
RULE #1 (MOST IMPORTANT)
=====================

TRADE ONLY AFTER LIQUIDITY SWEEP.

No sweep = wait.

=====================
BIAS (SIMPLE)
=====================

- Above EMA 50 → bullish bias
- Below EMA 50 → bearish bias

=====================
SETUP LOGIC
=====================

BUY:
- Price sweeps LOW (sell-side liquidity)
- Then MSS UP
- Then return to FVG
→ BUY from discount

SELL:
- Price sweeps HIGH (buy-side liquidity)
- Then MSS DOWN
- Then return to FVG
→ SELL from premium

=====================
ENTRY
=====================

- Wait for pullback into FVG
- Entry must be tight zone
- No chasing

=====================
SL / TP
=====================

SL:
- beyond liquidity

TP:
- next liquidity

RR:
- minimum 1:2

=====================
IMPORTANT
=====================

- Ignore weak setups
- Ignore mid range
- Focus only on clean sweep + MSS

- If not ready:
→ give WAIT scenario (but still define entry condition)

⚠️ NEVER always SELL or always BUY.
⚠️ Direction MUST follow liquidity sweep + MSS.

=====================
OUTPUT
=====================

Direction: BUY or SELL

WAIT FOR:
(clear sweep + MSS + level)

Entry Zone:
(price range)

Stop Loss:
(price)

Take Profit:
(price)

No explanation.
"""

# 🔄 RESET COMMAND
@bot.message_handler(commands=['reset'])
def reset(message):
    user_data[message.chat.id] = []
    bot.send_message(message.chat.id, "Reset yapıldı 🔄")

# 📸 FOTO HANDLER
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    filename = f"{user_id}.jpg"
    with open(filename, "wb") as f:
        f.write(downloaded_file)

    with open(filename, "rb") as img:
        b64 = base64.b64encode(img.read()).decode()

    if user_id not in user_data:
        user_data[user_id] = []

    user_data[user_id].append(b64)

    # 1. foto
    if len(user_data[user_id]) == 1:
        bot.send_message(user_id, "HTF geldi 👍 şimdi LTF at")
        return

    # 2. foto → ANALİZ
    if len(user_data[user_id]) == 2:

        htf = user_data[user_id][0]
        ltf = user_data[user_id][1]

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
                            "image_url": f"data:image/jpeg;base64,{htf}"
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{ltf}"
                        }
                    ]
                }]
            )

            bot.send_message(user_id, response.output_text)

        except Exception as e:
            bot.send_message(user_id, f"Hata: {e}")

        user_data[user_id] = []

bot.polling()