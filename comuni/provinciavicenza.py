### Comune di vicenza ###
### Sostituisci "vicenza" con il nome del Comune ###

import asyncio
from datetime import datetime
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
import io
from playwright.async_api import async_playwright

# 🔧 CONFIGURAZIONE
COMUNE = "vicenza"
BASE_URL = f"https://www.provincia.{COMUNE}.it"
FEED_FILE = f"feeds/provincia{COMUNE}.xml"
SOURCE_URL = BASE_URL

# 🔧 FUNZIONI DI SUPPORTO

def normalize_url(raw_url, base_url):
    if not raw_url:
        return None
    raw_url = raw_url.strip()

    if raw_url.startswith("http://") or raw_url.startswith("https://"):
        return raw_url
    if "municipiumapp.it" in raw_url or "cloudfront.net" in raw_url:
        return "https://" + raw_url.lstrip("/")

    return urljoin(base_url + "/", raw_url.lstrip("/"))

async def find_image(block, base_url):
    selectors = [
        "img.img-fluid",
        "img.img-responsive",
        "img.img-object-fit-contain",
        "img"
    ]
    for selector in selectors:
        img_el = await block.query_selector(selector)
        if img_el:
            raw_src = await img_el.get_attribute("src")
            if raw_src:
                return normalize_url(raw_src, base_url)
    print("⚠️ Nessuna immagine trovata nel blocco")
    return None

async def find_description(block):
    selectors = [
        "p.card-text div",
        "p.card-text",
        "div.card-body",
        "div.text",
        "h3",
        "div"
    ]
    for selector in selectors:
    #    el = await block.query_selector(selector)
    #    if el:
    #        text = await el.inner_text()
    #        if text.strip():
    #            return text.strip()
        print("⚠️ Nessuna descrizione trovata")
    return ""

# 🔍 ESTRAZIONE DATI

async def fetch_news():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = await context.new_page()
        await page.goto(SOURCE_URL, timeout=60000)
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)

        blocks = await page.query_selector_all("dd.portletItem.withImg")
        print(f"🔢 Trovati {len(blocks)} blocchi")
        news_items = []

        for block in blocks[:10]:
            title_el = await block.query_selector("h4")
            date_el = await block.query_selector("span.itemdata")
            link_el = await block.query_selector("a")

            title = (await title_el.inner_text()) if title_el else "Senza titolo"
            if title.lower() in ["avvisi", "notizie", "comunicati"]:
                continue

            date_text = (await date_el.inner_text()) if date_el else ""
            link = (await link_el.get_attribute("href")) if link_el else "#"
            link = normalize_url(link, BASE_URL)

            try:
                pub_date = datetime.strptime(date_text, "%d %b %Y") if date_text else datetime.now()
            except:
                pub_date = datetime.now()

            description = await find_description(block)
            img_src = await find_image(block, BASE_URL)

            news_items.append({
                "title": title.strip(),
                "link": link.strip(),
                "date": pub_date,
                "description": description.strip(),
                "image": img_src
            })

        await browser.close()
        return news_items

# 📰 GENERAZIONE RSS

def generate_feed():
    news_items = asyncio.run(fetch_news())

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = f"Comune di {COMUNE} - Notizie"
    ET.SubElement(channel, "link").text = SOURCE_URL
    ET.SubElement(channel, "description").text = f"Ultime notizie dal sito ufficiale del Comune di {COMUNE}"
    ET.SubElement(channel, "language").text = "it"

    for item in news_items:
        entry = ET.SubElement(channel, "item")
        ET.SubElement(entry, "title").text = item["title"]
        ET.SubElement(entry, "link").text = item["link"]
        ET.SubElement(entry, "pubDate").text = item["date"].strftime("%a, %d %b %Y %H:%M:%S GMT")

        desc_text = item.get("description", "")
        img_tag = f'<img src="{item["image"]}" alt="immagine" style="max-width:100%;"/><br/>' if item.get("image") else ""
        ET.SubElement(entry, "description").text = img_tag + desc_text

    tree = ET.ElementTree(rss)
    tree.write(FEED_FILE, encoding="utf-8", xml_declaration=True)

    output = io.BytesIO()
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return output.getvalue().decode("utf-8")

# 🚀 AVVIO SCRIPT

if __name__ == "__main__":
    content = generate_feed()
    print(f"✅ Feed generato con {content.count('<item>')} notizie (max 10).")
