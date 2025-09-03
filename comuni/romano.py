import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import os

FEED_FILE = os.path.join("feeds", "romano.xml")
URL_API = "https://www.comune.romano.vi.it/myportal/C_H512/api/content"
PARAMS = {
    "type": "pnrr_news",
    "pageIndex": 1,
    "onlyNotHidden": "true",
    "parent": "/",
    "includeSubFolders": "true",
    "sortBy": "pubDate",
    "desc": "true",
    "pageSize": 20,
    "excludedPnrrTaxonomiesFilter": "true"
}
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0"
}

def fetch_articles():
    r = requests.get(URL_API, params=PARAMS, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    articles = []
    for entity in data.get("page", {}).get("entities", []):
        attr = entity.get("attributes", {})    
        title = attr.get("sys_title", "")
        slug = attr.get("sys_canonical_url") or ("/news/" + attr.get("sys_slug", ""))
        link = "https://www.comune.romano.vi.it" + slug
        description = attr.get("sys_description", "")
        date_str = attr.get("sys_sottotitolo", "")
        
        # print per debug 
        #print(f"Trovata notizia: {title} → {link}")

        try:
            pub_date = datetime.strptime(date_str, "%d %B %Y")
            pub_date = pub_date.replace(tzinfo=timezone.utc)
        except:
            pub_date = datetime.now(timezone.utc)
        articles.append({
            "title": title,
            "link": link,
            "description": description,
            "pubDate": pub_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        })
    return articles

def generate_feed():
    articles = fetch_articles()
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Comune di Romano d'Ezzelino - Notizie"
    ET.SubElement(channel, "link").text = "https://www.comune.romano.vi.it/home/novita"
    ET.SubElement(channel, "description").text = "Feed RSS simulato"
    
    for art in articles:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = art["title"]
        ET.SubElement(item, "link").text = art["link"]
        ET.SubElement(item, "description").text = art["description"]
        ET.SubElement(item, "pubDate").text = art["pubDate"]
    
    os.makedirs(os.path.dirname(FEED_FILE), exist_ok=True)
    tree = ET.ElementTree(rss)
    tree.write(FEED_FILE, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    print("Inizio generazione feed per Comune di Romano d'Ezzelino")
    generate_feed()
    print(f"Feed generato correttamente: {FEED_FILE}")
