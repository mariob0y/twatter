import asyncio
import os
import telebot
from flask import Flask, request
from tweetcapture import TweetCapture
from urlextract import URLExtract
from youtube_dl.YoutubeDL import YoutubeDL
from youtube_dl.utils import DownloadError, UnsupportedError

app = Flask(__name__)


telebot.apihelper.ENABLE_MIDDLEWARE = True
TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
DOMAIN = os.environ.get("DOMAIN", "")

bot = telebot.TeleBot(TOKEN)
extractor = URLExtract()
tweet = TweetCapture()
downloader = YoutubeDL(params={"outtmpl": "video.mp4", "extract_flat": "in_playlist"})


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.from_user.id, "Welcome to Twatter")


@bot.message_handler(func=lambda message: True)
def get_text_messages(message):
    text = message.text
    message_id = message.message_id
    chat_id = message.chat.id

    image = "tweet.png"
    video_mp4 = "video.mp4"
    video_mkv = "video.mkv"
    urls = extractor.find_urls(text)

    for file in (image, video_mp4, video_mkv):
        if os.path.exists(file):
            os.remove(file)

    for url in urls:
        if url.startswith(
            ("youtube", "www.youtube", "https://youtube", "https://youtube")
        ):
            return
        if url.startswith(("twitter", "www")):
            url = "https://" + url
        try:
            downloader.download([url])
            _file = video_mp4 if os.path.exists(video_mp4) else video_mkv
            with open(_file, "rb") as _video:
                bot.send_video(
                    chat_id,
                    _video,
                    reply_to_message_id=message_id,
                    supports_streaming=True,
                )
                return
        except (DownloadError, UnsupportedError):

            asyncio.run(tweet.screenshot(url, image, mode=4, night_mode=1))
            with open(image, "rb") as _image:
                try:
                    bot.send_photo(chat_id, _image, reply_to_message_id=message_id)
                except Exception as e:
                    return


# bot.infinity_polling(none_stop=True, interval=1)
@app.route("/" + TOKEN, methods=["POST"])
def getMessage():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=DOMAIN + TOKEN)
    return "!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
