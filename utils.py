import os


def clear_video_file():
    for file in os.listdir("."):
        if file.endswith((".mp4", ".mkv")):
            os.remove(file)


def get_video_file():
    _file = ""
    for file in os.listdir("."):
        if file.endswith((".mp4", ".mkv")):
            _file = file
    return _file


def prepare_urls(urls):
    for index, url in enumerate(urls):
        if url.startswith(("twitter", "www")):
            urls[index] = "https://" + url
    return urls
