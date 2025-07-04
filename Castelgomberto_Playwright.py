from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
import time

def genera_feed_castelgomberto():
    print("\n➡️ Inizio generazione feed per Comune di Castelgomberto (da /home/novita)")

    try:
        url = "https://www.comune.castelgomberto.vi.it/home/novita"
        base_url = "https://www.comune.castelgomberto.vi.it"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  
            page = browser.new_page()
            page.goto(url, timeout=60000)
            time.sleep(5)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("div.card-wrapper")
        print(f"🔎 Trovati {len(cards)} elementi con selector 'div.card-wrapper'\n")

        fg = FeedGenerator()
        fg.title("Comune di Castelgomberto - Novità")
        fg.link(href=url, rel="alternate")
        fg.description("Ultime notizie dal sito ufficiale del Comune di Castelgomberto")

        titoli_visti = set()
        valid_count = 0

        for i, card in enumerate(cards, 1):
            print(f"📦 Card {i}")
            title_tag = card.select_one("h3.card-title")
            link_tag = card.select_one("a[href]")

            if not title_tag or not link_tag:
                print("❌ Card scartata: mancano <h3> o <a>\n")
                continue

            title = title_tag.get_text(strip=True)
            if not title or title.lower() in ["avvisi", "notizie", "comunicati"]:
                print(f"⏭️ Escluso: {title}\n")
                continue

            if title in titoli_visti:
                print("🔁 Titolo già visto, salto\n")
                continue
            titoli_visti.add(title)

            href = link_tag.get("href")
            if href.startswith("/home/novita"):
                href = href.replace("/home/novita", "")

            full_link = urljoin(base_url, href)
            print(f"🟢 Titolo: {title}")
            print(f"🔗 Link: {full_link}\n")

            pubdate = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

            fe = fg.add_entry()
            fe.id(full_link)
            fe.title(title)
            fe.link(href=full_link)
            fe.pubDate(pubdate)
            valid_count += 1

        if valid_count > 0:
            fg.rss_file("castelgomberto.xml")
            print(f"✅ Feed generato → castelgomberto.xml con {valid_count} articoli")
        else:
            print("⚠️ Nessun elemento valido trovato per il feed.")

    except Exception as e:
        print(f"❌ Errore feed Castelgomberto: {e}")

if __name__ == "__main__":
    genera_feed_castelgomberto()
