###  Sostituisci vicenza con il nome del Comune ###
###  Comune di vicenza

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import xml.etree.ElementTree as ET
import io

FEED_FILE = "feeds/vicenza.xml"
URL = "https://www.comune.vicenza.it/Novita"

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
        await page.goto(URL, timeout=60000)
        await page.wait_for_load_state('networkidle') 
        await asyncio.sleep(2)

        blocks = await page.query_selector_all("div.px-3.pb-3")
        print(f"🔢 Trovati {len(blocks)} blocchi")
        news_items = []

        for block in blocks[:10]:
            html = await block.inner_html()
            ##print(f"\n🔍 HTML del blocco:\n{html}\n")


            title_el = await block.query_selector("h3")
            date_el = await block.query_selector("span.fw-normal")
            link_el = await block.query_selector("a")

            title = (await title_el.inner_text()) if title_el else "Senza titolo"

            if title.lower() in ["avvisi", "notizie", "comunicati"]:
                #print(f" Escluso: {title}\n")
                continue
            
            date_text = (await date_el.inner_text()) if date_el else ""
            link = (await link_el.get_attribute("href")) if link_el else "#"

            if link and link.startswith("/"):
                link = "https://www.comune.vicenza.it" + link

            pub_date = None
            if date_text:
                try:
                    pub_date = datetime.strptime(date_text, "%d %b %Y")
                except:
                    pub_date = datetime.now()

            # Descrizione corretta
            desc_el = await block.query_selector("div.card-text div")
            description = ""
            if desc_el:
                description = await desc_el.inner_text()
                #print(f"📝 Descrizione trovata: {description}")

            # Immagine corretta
            img_el = await block.query_selector("img.img-responsive")
            img_src = None
            if img_el:
                img_src = await img_el.get_attribute("src")
                #print(f"🖼️ Immagine trovata: {img_src}")
                if img_src and img_src.startswith("/"):
                    img_src = "https://www.comune.vicenza.it" + img_src

            ####################################

            news_items.append({
                "title": title.strip(),
                "link": link.strip(),
                "date": pub_date or datetime.now(),
                "description": description.strip(),
                "image": img_src
            })

        await browser.close()
        return news_items

def generate_feed(site=None):
    news_items = asyncio.run(fetch_news())

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Comune di Vicenza - Notizie"
    ET.SubElement(channel, "link").text = URL
    ET.SubElement(channel, "description").text = "Ultime notizie dal sito ufficiale del Comune di Vicenza"
    ET.SubElement(channel, "language").text = "it"

    for item in news_items:
        entry = ET.SubElement(channel, "item")
        ET.SubElement(entry, "title").text = item["title"]
        ET.SubElement(entry, "link").text = item["link"]
        ET.SubElement(entry, "pubDate").text = item["date"].strftime("%a, %d %b %Y %H:%M:%S GMT")

        # Descrizione con immagine
        desc_text = item.get("description", "")
        img_tag = f'<img src="{item["image"]}" alt="immagine" style="max-width:100%;"/><br/>' if item.get("image") else ""
        ET.SubElement(entry, "description").text = img_tag + desc_text

    tree = ET.ElementTree(rss)
    tree.write(FEED_FILE, encoding="utf-8", xml_declaration=True)

    output = io.BytesIO()
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return output.getvalue().decode("utf-8")

if __name__ == "__main__":
    content = generate_feed()
    print(f"✅ Feed generato con {content.count('<item>')} notizie (max 10).")
