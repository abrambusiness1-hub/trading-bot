import telebot
from openai import OpenAI
import base64

# 🔑 BURAYA KENDİ TOKENLERİNİ KOY
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

    # 1. foto (HTF)
    if len(user_data[user_id]) == 1:
        bot.send_message(user_id, "HTF geldi 👍 şimdi LTF at")
        return

    # 2. foto (LTF) → analiz
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
                            "text": """You are a professional ICT (Inner Circle Trader) trader.

You analyze TWO charts:
- First image = HTF (1H or 4H)
- Second image = LTF (5m or 15m)

=====================
CORE LOGIC
=====================

Use EMA 50 & 200:
- Above = bullish
- Below = bearish

Liquidity:
- Highs = buy liquidity
- Lows = sell liquidity

MSS:
- Required confirmation
- Break structure before entry

FVG:
- Use fresh imbalance zones
- Entry inside FVG

IFVG:
- Broken FVG becomes S/R

Premium / Discount:
- Above 50% → SELL
- Below 50% → BUY

=====================
ENTRY RULES
=====================

BUY:
- HTF bullish
- Liquidity taken below
- MSS up
- Entry at FVG in discount

SELL:
- HTF bearish
- Liquidity taken above
- MSS down
- Entry at FVG in premium

=====================
EXECUTION
=====================

- NEVER chase candles
- WAIT for pullback
- Entry must be zone
- SL beyond liquidity
- TP at next liquidity

RR:
- Minimum 1:2

=====================
OUTPUT
=====================

Direction: BUY or SELL

WAIT FOR:
(price to reach level)

Entry Zone:
(price range)

Stop Loss:
(price)

Take Profit:
(price)

No explanation."""
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