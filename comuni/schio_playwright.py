from playwright.sync_api import sync_playwright
from datetime import datetime
import xml.etree.ElementTree as ET
import os

SITE_INFO = {
    "name": "Comune di Schio",
    "url": "https://www.comune.schio.vi.it/Novita",
    "output": "feeds/feed_schio.xml"
}

def get_items():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SITE_INFO["url"], timeout=60000)

        # Accetta cookies se presenti
        try:
            page.click("button:has-text('Accetta')", timeout=5000)
            print("[OK] Cookies accettati")
        except:
            print("[INFO] Nessun banner cookies trovato")

        page.wait_for_timeout(3000)

        items = []
        cards = page.query_selector_all("div.card.card-teaser")
        print(f"Trovati {len(cards)} articoli.")

        for card in cards:
            title_elem = card.query_selector("h3.card-title")
            link_elem = card.query_selector("a.read-more")
            date_elem = card.query_selector("div:has-text('Data di pubblicazione')")

            title = title_elem.inner_text().strip() if title_elem else "Senza titolo"
            link = link_elem.get_attribute("href") if link_elem else SITE_INFO["url"]
            date_str = date_elem.inner_text().replace("Data di pubblicazione:", "").strip() if date_elem else ""
            try:
                pub_date = datetime.strptime(date_str, "%d/%m/%Y").strftime("%a, %d %b %Y")
            except:
                pub_date = datetime.now().strftime("%a, %d %b %Y")

            items.append({
                "title": title,
                "link": link,
                "pubDate": pub_date
            })

        browser.close()
        return items

def generate_feed():
    items = get_items()

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = SITE_INFO["name"]
    ET.SubElement(channel, "link").text = SITE_INFO["url"]
    ET.SubElement(channel, "description").text = f"Ultime notizie da {SITE_INFO['name']}"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S ")

    for item in items:
        item_elem = ET.SubElement(channel, "item")
        ET.SubElement(item_elem, "title").text = item["title"]
        ET.SubElement(item_elem, "link").text = item["link"]
        ET.SubElement(item_elem, "pubDate").text = item["pubDate"]

    os.makedirs(os.path.dirname(SITE_INFO["output"]), exist_ok=True)
    tree = ET.ElementTree(rss)
    tree.write(SITE_INFO["output"], encoding="utf-8", xml_declaration=True)
    print(f"[OK] Feed generato: {SITE_INFO['output']}")

if __name__ == "__main__":
    generate_feed()
