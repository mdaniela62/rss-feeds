# comuni/romano.py
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import xml.etree.ElementTree as ET

FEED_FILE = "feeds/romano.xml"
URL = "https://www.comune.romano.vi.it/home/novita.html"

async def fetch_news():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,  # rimane headless ma “camuffato”
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-gpu"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = await context.new_page()
        await page.goto(URL, timeout=60000)
        await page.wait_for_selector("div.col-md-6.col-xl-4", timeout=60000)

        blocks = await page.query_selector_all("div.col-md-6.col-xl-4")
        news_items = []

        for block in blocks[:5]:  # solo le prime 5 notizie
            title_el = await block.query_selector("h3")
            date_el = await block.query_selector("span.fw-normal")
            link_el = await block.query_selector("a")

            title = (await title_el.inner_text()) if title_el else "Senza titolo"
            date_text = (await date_el.inner_text()) if date_el else ""
            link = (await link_el.get_attribute("href")) if link_el else "#"

            if link and link.startswith("/"):
                link = "https://www.comune.romano.vi.it" + link

            pub_date = None
            if date_text:
                try:
                    pub_date = datetime.strptime(date_text, "%d %b %Y")
                except:
                    pub_date = datetime.now()

            news_items.append({
                "title": title.strip(),
                "link": link.strip(),
                "date": pub_date or datetime.now()
            })

        await browser.close()
        return news_items

def generate_rss(news_items):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Comune di Romano d’Ezzelino - Notizie"
    ET.SubElement(channel, "link").text = URL
    ET.SubElement(channel, "description").text = "Ultime notizie dal sito ufficiale del Comune di Romano d’Ezzelino"
    ET.SubElement(channel, "language").text = "it"

    for item in news_items:
        entry = ET.SubElement(channel, "item")
        ET.SubElement(entry, "title").text = item["title"]
        ET.SubElement(entry, "link").text = item["link"]
        ET.SubElement(entry, "pubDate").text = item["date"].strftime("%a, %d %b %Y %H:%M:%S GMT")

    tree = ET.ElementTree(rss)
    tree.write(FEED_FILE, encoding="utf-8", xml_declaration=True)

async def main():
    news = await fetch_news()
    generate_rss(news)
    print(f"✅ Feed generato con {len(news)} notizie (max 5).")

if __name__ == "__main__":
    asyncio.run(main())

