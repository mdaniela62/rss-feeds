import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import re
import os

FEED_TITLE = "Feed RSS simulato"
FEED_DESCRIPTION = "Feed generato automaticamente"
FEED_LINK = "https://github.com/mdaniela62/rss-feeds"

def slugify(url):
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '_')
    path = re.sub(r'[^a-zA-Z0-9]', '_', parsed.path)
    return f"{domain}{path}.xml"

def extract_articles(url):
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"Errore nel recupero di {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.get_text(strip=True)
        if href and text and len(text) > 5:
            if not href.startswith('http'):
                href = url + href
            articles.append({'title': text, 'link': href})
    
    return articles[:10]  # Limitiamo a 10 articoli per feed

def create_rss(articles, site_url):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = FEED_TITLE
    ET.SubElement(channel, "description").text = FEED_DESCRIPTION
    ET.SubElement(channel, "link").text = site_url

    for article in articles:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article['title']
        ET.SubElement(item, "link").text = article['link']

    return ET.tostring(rss, encoding='utf-8', xml_declaration=True)

def main():
    if not os.path.exists("sites.txt"):
        print("Il file sites.txt non esiste.")
        return

    with open("sites.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        print(f"Generazione feed per: {url}")
        articles = extract_articles(url)
        rss_content = create_rss(articles, url)
        filename = slugify(url)
        with open(filename, "wb") as f:
            f.write(rss_content)
        print(f"Feed generato: {filename}")

if __name__ == "__main__":
    main()
