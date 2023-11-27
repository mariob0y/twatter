import asyncio
import telebot
from tweetcapture import TweetCapture
from urlextract import URLExtract
from youtube_dl.YoutubeDL import YoutubeDL
from youtube_dl.utils import DownloadError, UnsupportedError
from const import TOKEN, IMAGE_FILE
from utils import clear_output_files, get_video_file, prepare_urls
from screenshot import save_screenshot
import imghdr
from cleanurl import cleanurl


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
    clear_output_files()

    text = message.text
    message_id = message.message_id
    chat_id = message.chat.id

    urls = url_extractor.find_urls(text)
    prepare_urls(urls)

    for url in urls:
        url = cleanurl(url, respect_semantics=True)
        url = f'{url.hostname}{url.path}'
        try:
            # Sometimes yt downloader
            video_downloader.download([url])
            video_file = get_video_file()
            if imghdr.what(video_file):
                asyncio.run(save_screenshot(url))
                with open(IMAGE_FILE, "rb") as _image:
                    bot.send_photo(chat_id, _image, reply_to_message_id=message_id)
            else:
                with open(video_file, "rb") as video:
                    bot.send_video(
                        chat_id,
                        video,
                        reply_to_message_id=message_id,
                        supports_streaming=True,
                    )

        except (DownloadError, UnsupportedError):
            try:
                asyncio.run(save_screenshot(url))
                with open(IMAGE_FILE, "rb") as _image:
                    bot.send_photo(chat_id, _image, reply_to_message_id=message_id)
            except Exception as e:
                try:
                    asyncio.run(
                        tweet_capture.screenshot(url, IMAGE_FILE, mode=4, night_mode=1)
                    )
                    with open(IMAGE_FILE, "rb") as _image:
                        bot.send_photo(chat_id, _image, reply_to_message_id=message_id)
                except Exception as e:
                    print(f"Unsupported URL: {url}")

        inst_reel_str = "instagram.com/reel"
        inst_reel_str_fixed = f'dd{inst_reel_str}'
        if inst_reel_str in url and inst_reel_str_fixed not in url:
            url = url.replace(inst_reel_str, inst_reel_str_fixed)
            bot.send_message(chat_id, url, reply_to_message_id=message_id)

        twtr_strs = ['mobile.twitter.com', 'mobile.x.com', 'twitter.com', 'x.com']
        twtr_str_fixed = 'fxtwitter.com'
        for twtr_str in twtr_strs:
            if twtr_str in url and twtr_str_fixed not in url:
                _url = url.replace(twtr_str, twtr_str_fixed)
                bot.send_message(chat_id, _url, reply_to_message_id=message_id)
                break


if __name__ == "__main__":
    # for local run
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True, interval=1)
