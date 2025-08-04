import requests
from bs4 import BeautifulSoup
from datetime import datetime

SITE_INFO = {
    "name": "Comune di Schio",
    "url": "https://www.comune.schio.vi.it/Novita",
    "output": "feeds/feed_schio.xml"
}

def get_items():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(SITE_INFO["url"], headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    articles = soup.select("div.card-teaser, div.card.card-teaser-image")
    items = []

    for article in articles:
        title_tag = article.select_one("h3.card-title")
        link_tag = article.select_one("a.read-more")
        description_tag = article.select_one("div.text-paragraph-card")
        date_tag = article.find("strong", string=lambda t: "Data di pubblicazione" in t)

        title = title_tag.get_text(strip=True) if title_tag else "Senza titolo"
        link = link_tag["href"] if link_tag else "/"
        if not link.startswith("http"):
            link = "https://www.comune.schio.vi.it" + link
        description = description_tag.get_text(strip=True) if description_tag else ""
        pub_date = ""
        if date_tag and date_tag.next_sibling:
            raw_date = date_tag.next_sibling.strip()
            try:
                pub_date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%a, %d %b %Y")
            except:
                pass
        items.append({
            "title": title,
            "link": link,
            "description": description,
            "pubDate": pub_date
        })
    return items
