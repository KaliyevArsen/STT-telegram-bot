import telebot
import requests
import random
import os
from openai import OpenAI
from pydub import AudioSegment

TELEGRAM_TOKEN = ''
bot = telebot.TeleBot(TELEGRAM_TOKEN)
OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY",
    "")
client = OpenAI(api_key=OPENAI_API_KEY)


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        file_path = file_info.file_path
        file_url = f'https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}'

        # download audio message
        response = requests.get(file_url)
        if response.status_code != 200:
            return

        ogg_filename = f"{random.randint(0, 100000)}.ogg"

        # saving file localy
        with open(ogg_filename, 'wb') as f:
            f.write(response.content)

        # converting .ogg to .mp3
        mp3_filename = f"{random.randint(0, 100000)}.mp3"
        audio = AudioSegment.from_file(ogg_filename, format="ogg")
        audio.export(mp3_filename, format="mp3")

        # open mp3 and transcribe
        audio_file = open(mp3_filename, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        bot.reply_to(message, transcription)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

    finally:
        if os.path.exists(ogg_filename):
            os.remove(ogg_filename)
        if os.path.exists(mp3_filename):
            os.remove(mp3_filename)

if __name__ == '__main__':
    bot.polling()
