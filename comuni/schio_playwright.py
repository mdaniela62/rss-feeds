from playwright.sync_api import sync_playwright
from datetime import datetime

SITE_INFO = {
    "name": "Comune di Schio (Playwright)",
    "url": "https://www.comune.schio.vi.it/Novita",
    "output": "feeds/feed_schio.xml"
}

def get_items():
    items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SITE_INFO["url"], timeout=15000)

        page.wait_for_selector("div.card-teaser, div.card.card-teaser-image", timeout=10000)

        articles = page.query_selector_all("div.card-teaser, div.card.card-teaser-image")
        for article in articles:
            title_tag = article.query_selector("h3.card-title")
            link_tag = article.query_selector("a.read-more")
            description_tag = article.query_selector("div.text-paragraph-card")
            date_tag = article.query_selector("strong")

            title = title_tag.inner_text().strip() if title_tag else "Senza titolo"
            link = link_tag.get_attribute("href") if link_tag else "/"
            if not link.startswith("http"):
                link = "https://www.comune.schio.vi.it" + link
            description = description_tag.inner_text().strip() if description_tag else ""
            pub_date = ""

            if date_tag and "Data di pubblicazione" in date_tag.inner_text():
                raw = date_tag.evaluate("el => el.nextSibling?.textContent") or ""
                raw = raw.strip()
                try:
                    pub_date = datetime.strptime(raw, "%d/%m/%Y").strftime("%a, %d %b %Y")
                except:
                    pass

            items.append({
                "title": title,
                "link": link,
                "description": description,
                "pubDate": pub_date
            })

        browser.close()
    return items

if __name__ == "__main__":
    print(f"➡️  Eseguo Playwright per: {SITE_INFO['url']}")
    articoli = get_items()
    print(f"Trovati {len(articoli)} articoli.")
    for a in articoli[:5]:
        print("-", a["title"])
