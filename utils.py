import os
from urllib.parse import urlparse


def clear_output_files():
    for file in os.listdir("."):
        if file.endswith((".mp4", ".mkv", ".png")):
            os.remove(file)


def get_video_file():
    _file = ""
    for file in os.listdir("."):
        if file.endswith((".mp4", ".mkv")):
            _file = file
    return _file


def prepare_urls(urls):
    for index, url in enumerate(urls):
        if url.startswith("www"):
            urls[index] = "https://" + url
        # instagram specific
        if "instagram.com" in url:
            if "?hl=" in url:
                prefix, _, postfix = url.partition("?hl=")
                urls[index] = prefix + "?hl=uk"
            else:
                urls[index] = url + "?hl=uk" if url.endswith("/") else url + "/?hl=uk"
    return urls


def get_url_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc
