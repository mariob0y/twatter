import asyncio
from playwright.async_api import async_playwright
from const import IMAGE_FILE
from utils import get_url_domain


MAX_COMMENT_LIMIT = 10


async def capture_instagram(browser, url):
    page = await browser.new_page()

    await page.goto(url)
    posts = page.locator("article")

    try:
        # try to load comments from post if such are present
        comments = page.locator('[aria-label="Завантажити більше коментарів"]')
        await asyncio.wait_for(comments.first.is_enabled(), timeout=10.0)
    except asyncio.exceptions.TimeoutError:
        pass

    popup = page.locator('[aria-label="Закрити"]')
    await popup.first.click()
    await posts.first.screenshot(path="post.png")


async def capture_twitter(browser, url):
    page = await browser.new_page()

    await page.goto(url)
    post = page.locator("data-testid=tweet").first
    # Remove bottom bar with login reminder
    await page.eval_on_selector(
        selector="data-testid=BottomBar",
        expression="(el) => el.style.display = 'none'",
    )
    await post.screenshot(path="post.png")


async def capture_reddit(browser, url):
    page = await browser.new_page()
    await page.goto(url)
    # Remove top search bar
    await page.eval_on_selector(
        selector="header",
        expression="(el) => el.style.display = 'none'",
    )
    posts = page.locator("data-testid=post-container")
    await posts.first.screenshot(path=IMAGE_FILE)


methods = {
    "www.instagram.com": capture_instagram,
    "www.twitter.com": capture_twitter,
    "www.reddit.com": capture_reddit,
}


async def save_screenshot(url):
    async with async_playwright() as p:
        capture_method = methods.get(get_url_domain(url), None)
        if not capture_method:
            return
        browser = await p.chromium.launch()
        await capture_method(browser, url)
        await browser.close()
