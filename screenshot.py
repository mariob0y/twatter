import asyncio
from playwright.async_api import async_playwright, Browser
from const import IMAGE_FILE, LOCATORS
from utils import get_url_domain
from tweetcapture import TweetCapture

tweet_capture = TweetCapture()

MAX_COMMENT_LIMIT = 10


async def capture(browser: Browser, url, locator):
    page = await browser.new_page()
    await page.goto(url)
    posts = page.locator(locator)
    await posts.first.screenshot(path=IMAGE_FILE)


async def screenshot(url, locator):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        await capture(browser, url, locator)
        await browser.close()


def make_screenshot(url):
    domain = get_url_domain(url)
    locator = LOCATORS.get(domain, None)
    if locator:
        asyncio.run(screenshot(url, locator))
    else:
        asyncio.run(tweet_capture.screenshot(url, IMAGE_FILE, mode=4, night_mode=1))
