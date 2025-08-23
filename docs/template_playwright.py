import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
from datetime import datetime

async def generate_feed(url, output_file):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        # Prendi l'HTML reso dal browser
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Feed di base
    feed = Rss201rev2Feed(
        title="Feed RSS simulato (dinamico)",
        link=url,
        description="Notizie generate automaticamente",
        language="it"
    )

    # 🔧 Adatta qui ai selettori reali del sito
    articles = soup.select("h3.card-title")
    for art in articles:
        a = art.find("a")
        if not a:
            continue

        title = a.get_text(strip=True)
        link = a["href"]
        if link.startswith("/"):
            link = url.rstrip("/") + link

        # Data
        date_tag = art.find_next("span", class_="data")
        pub_date = None
        if date_tag:
            try:
                pub_date = datetime.strptime(
                    date_tag.get_text(strip=True), "%A, %d %B %Y"
                )
            except Exception:
                pass

        description = ""

        feed.add_item(
            title=title,
            link=link,
            description=description,
            pubdate=pub_date
        )

    with open(output_file, "w", encoding="utf-8") as f:
        feed.write(f, "utf-8")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Uso: python template_playwright.py <url> <output.xml>")
    else:
        asyncio.run(generate_feed(sys.argv[1], sys.argv[2]))
