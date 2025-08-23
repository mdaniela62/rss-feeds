import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import os

SITE_INFO = {
    "name": "Comune di NomeComune",
    "url": "URL_NOTIZIE",  # risposta alla domanda 1
    "feed": "feeds/feed_nomecomune.xml"
}

def get_items():
    resp = requests.get(SITE_INFO["url"])
    soup = BeautifulSoup(resp.text, "html.parser")

    items = []
    for articolo in soup.select("SELETTORE_CONTENITORE"):  # risposta 2
        titolo_elem = articolo.select_one("SELETTORE_TITOLO")  # risposta 3
        if not titolo_elem:
            continue

        titolo = titolo_elem.get_text(strip=True)
        link = titolo_elem["href"]
        if not link.startswith("http"):
            link = "https://www.comune.nomecomune.it" + link  # risposta 6

        data_elem = articolo.select_one("SELETTORE_DATA")  # risposta 4
        data_pub = data_elem.get_text(strip=True) if data_elem else ""

        desc_elem = articolo.select_one("SELETTORE_DESCRIZIONE")  # risposta 5
        descrizione = desc_elem.get_text(strip=True) if desc_elem else ""

        items.append({
            "title": titolo,
            "link": link,
            "pubDate": data_pub,
            "description": descrizione
        })

    return items

def generate_feed():
    items = get_items()
    fg = FeedGenerator()
    fg.title(SITE_INFO["name"])
    fg.link(href=SITE_INFO["url"], rel="alternate")
    fg.description(f"RSS simulato per {SITE_INFO['name']}")

    for item in items:
        fe = fg.add_entry()
        fe.title(item["title"])
        fe.link(href=item["link"])
        if item["pubDate"]:
            fe.pubDate(item["pubDate"])
        if item["description"]:
            fe.description(item["description"])

    os.makedirs("feeds", exist_ok=True)
    fg.rss_file(SITE_INFO["feed"])
