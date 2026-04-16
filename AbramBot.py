import telebot
from openai import OpenAI
import base64
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

user_data = {}

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

    if len(user_data[user_id]) == 1:
        bot.send_message(user_id, "HTF geldi 👍 şimdi LTF at")
        return

    if len(user_data[user_id]) == 2:
        htf = user_data[user_id][0]
        ltf = user_data[user_id][1]

        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Analyze charts and give trade setup (BUY/SELL, Entry, SL, TP). No explanation."},
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{htf}"},
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{ltf}"}
                    ]
                }]
            )

            bot.send_message(user_id, response.output_text)

        except Exception as e:
            bot.send_message(user_id, f"Hata: {e}")

        user_data[user_id] = []

# 🔥 CRASH OLURSA YENİDEN BAŞLASIN
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Bot crash:", e)