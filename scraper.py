# app/scraper.py
import re
import asyncio
import random
import traceback
from urllib.parse import urlparse, urljoin
from playwright.async_api import async_playwright

from config import EXCLUDED_PATTERNS

def should_visit(url, depth, domain, visited, max_depth):
    """
    Determines if a URL should be visited based on various criteria.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ['http', 'https']:
        return False
    if domain not in parsed.netloc:
        return False
    normalized_url = parsed.scheme + "://" + parsed.netloc + parsed.path
    if normalized_url in visited:
        return False
    if depth > max_depth:
        return False
    if any(p.search(url) for p in EXCLUDED_PATTERNS):
        return False
    return True

async def extract_page_content(page, url):
    """
    Extracts key content elements from a webpage.
    """
    try:
        title = await page.title()
        meta_description = await page.query_selector('meta[name="description"]')
        description = (await meta_description.get_attribute("content")).strip() if meta_description else "N/A"
        h1 = await page.text_content("h1") or "N/A"
        h2 = [await el.text_content() for el in await page.query_selector_all("h2")]
        h3 = [await el.text_content() for el in await page.query_selector_all("h3")]
        preview = "No content preview available."
        paragraphs = await page.query_selector_all("main p, article p, section p")
        for p in paragraphs[:3]:
            text = await p.inner_text()
            if len(text.strip()) > 50:
                preview = text.strip()
                break
        return {
            "url": url,
            "title": title,
            "description": description,
            "h1": h1,
            "h2_headings": h2,
            "h3_headings": h3,
            "content_preview": preview,
        }
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

async def worker(browser, queue, visited, data, max_depth, domain):
    """
    A worker task for the concurrent scraping process.
    """
    while True:
        try:
            url, depth = await queue.get()
            parsed = urlparse(url)
            normalized_url = parsed.scheme + "://" + parsed.netloc + parsed.path
            if normalized_url in visited or depth > max_depth:
                queue.task_done()
                continue
            visited.add(normalized_url)
            print(f"Scraping: {url}")

            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            page = await context.new_page()
            await page.route(re.compile(r"\.(png|jpg|jpeg|gif|svg|webp|woff|woff2|ttf|eot|otf)(\?.*)?$"), lambda route: route.abort())
            await asyncio.sleep(random.uniform(1, 2))
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("domcontentloaded")

            content = await extract_page_content(page, url)
            if content:
                data.append(content)

            links = await page.eval_on_selector_all("a", "els => els.map(a => a.href)")
            for link in links:
                abs_link = urljoin(url, link)
                if should_visit(abs_link, depth + 1, domain, visited, max_depth):
                    await queue.put((abs_link, depth + 1))

            await page.close()
            await context.close()
        except Exception as e:
            print("Scrape error:", e)
            traceback.print_exc()
        queue.task_done()

async def scrape_website(start_url, max_depth):
    """
    Main function to initiate the website crawling process.
    """
    queue = asyncio.Queue()
    await queue.put((start_url, 0))
    visited = set()
    scraped_data = []
    domain = urlparse(start_url).netloc

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        workers = [asyncio.create_task(worker(browser, queue, visited, scraped_data, max_depth, domain)) for _ in range(3)]
        await queue.join()
        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        await browser.close()
    return scraped_data