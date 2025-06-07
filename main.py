import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime

# URL dei siti da monitorare
SITES = {
    "altissimo": "https://www.comune.altissimo.vi.it/home/novita.html",
    "arzignano": "https://www.comune.arzignano.vi.it/home/novita.html"
}

def fetch_articles(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Errore nel recupero di {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []

    for article in soup.select("li.item, article, li"):  # prova con elementi comuni
        title = article.get_text(strip=True)
        link = article.find("a")
        href = link["href"] if link and link.has_attr("href") else url
        full_url = href if href.startswith("http") else os.path.join(url, href)
        if title:
            items.append((title, full_url))
    return items[:10]  # solo i primi 10

def build_feed(site_name, items):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = f"Feed - {site_name}"
    ET.SubElement(channel, "link").text = SITES[site_name]
    ET.SubElement(channel, "description").text = f"Notizie dal sito {site_name}"
    ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

    for title, link in items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = link
        ET.SubElement(item, "guid").text = link
        ET.SubElement(item, "pubDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

    tree = ET.ElementTree(rss)
    with open(f"{site_name}.xml", "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    for name, url in SITES.items():
        print(f"Generazione feed per {name}...")
        items = fetch_articles(url)
        build_feed(name, items)
