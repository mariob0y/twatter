import asyncio
import os
import telebot
from tweetcapture import TweetCapture
from urlextract import URLExtract
from youtube_dl.YoutubeDL import YoutubeDL
from youtube_dl.utils import DownloadError, UnsupportedError
from const import TOKEN, IMAGE_FILE
from utils import clear_video_file, get_video_file, prepare_urls


telebot.apihelper.ENABLE_MIDDLEWARE = True

bot = telebot.TeleBot(TOKEN)
url_extractor = URLExtract()
tweet_capture = TweetCapture()
video_downloader = YoutubeDL(
    params={"outtmpl": "video.mp4", "extract_flat": "in_playlist"}
)


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.from_user.id, "Welcome to Twatter")


@bot.message_handler(func=lambda message: True)
def get_text_messages(message):
    clear_video_file()

    text = message.text
    message_id = message.message_id
    chat_id = message.chat.id

    urls = url_extractor.find_urls(text)
    prepare_urls(urls)

    for url in urls:
        try:
            video_downloader.download([url])
            with open(get_video_file(), "rb") as video:
                bot.send_video(
                    chat_id,
                    video,
                    reply_to_message_id=message_id,
                    supports_streaming=True,
                )
        except (DownloadError, UnsupportedError):
            try:
                asyncio.run(
                    tweet_capture.screenshot(url, IMAGE_FILE, mode=4, night_mode=1)
                )
                with open(IMAGE_FILE, "rb") as _image:
                    bot.send_photo(chat_id, _image, reply_to_message_id=message_id)
            except Exception as e:
                print(f"Unsupported URL: {url}")


if __name__ == "__main__":
    # for local run
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True, interval=1)
