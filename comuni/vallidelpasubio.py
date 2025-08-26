import sys
import os
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Aggiungo il path corretto per importare generate_rss
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_rss import create_rss

SITE_URL = "https://www.comune.vallidelpasubio.vi.it/Novita"

def get_items():
    items = []
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(SITE_URL, timeout=60000)

        # Aspetto che ci siano notizie caricate
        page.wait_for_selector("div.card-body h3.card-title a.text-decoration-none", timeout=20000)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Ogni notizia è dentro un div.card-body
    for article in soup.select("div.card-body"):
        title_tag = article.select_one("h3.card-title a.text-decoration-none")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag.get("href")
        if not link.startswith("http"):
            link = "https://www.comune.vallidelpasubio.vi.it" + link

        # Data
        date_tag = article.select_one("small.text-muted")
        if date_tag:
            try:
                pub_date = datetime.strptime(date_tag.get_text(strip=True), "%d/%m/%Y")
            except:
                pub_date = datetime.now()
        else:
            pub_date = datetime.now()

        items.append({
            "title": title,
            "link": link,
            "description": title,
            "pub_date": pub_date,
        })

    return items

def generate_feed(site=None):
    items = get_items()
    create_rss(
        "Comune di Valli del Pasubio - Notizie",
        SITE_URL,
        "Ultime notizie dal sito del Comune di Valli del Pasubio",
        items,
        "vallidelpasubio.xml"
    )

if __name__ == "__main__":
    generate_feed()
