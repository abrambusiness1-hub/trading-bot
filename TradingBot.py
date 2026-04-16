import telebot
from openai import OpenAI
import base64

# 🔑 TOKENLER
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

user_data = {}

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
        bot.send_message(user_id, "İkinci chartı gönder (HTF + LTF birlikte analiz)")
        return

    # 2. foto → ANALİZ
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
                            "text": """You are an elite ICT sniper trader with a focus on high win-rate setups (70–80% accuracy).

You will receive TWO chart images.

AUTO DETECT:
- Chart with smoother structure = HTF
- Chart with more candles = LTF

=====================
CORE SYSTEM (SNIPER MODE)
=====================

Only A+ setups.

REQUIRED:
- HTF bias (EMA 50 & 200)
- Liquidity sweep
- Strong MSS
- Clean FVG entry

=====================
HTF
=====================

- EMA 50/200 trend
- Liquidity (highs/lows)
- Target = draw on liquidity

=====================
LTF ENTRY
=====================

1. Liquidity sweep
2. MSS (strong break)
3. FVG entry
4. Pullback (NO chasing)

=====================
RULES
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
- liquidity sweep level
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

NO explanation."""
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

        user_data[user_id] = []

bot.polling()