import os

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
DOMAIN = os.environ.get("DOMAIN", "")
IMAGE_FILE = "post.png"
LOCATORS = {"www.reddit.com": "data-testid=post-container"}
