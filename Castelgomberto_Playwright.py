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
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                java_script_enabled=True
            )
            page = context.new_page()
            page.goto(url, timeout=60000)

            # Trucchetto anti-bot per siti che controllano headless
            page.evaluate("""() => {
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            }""")

            try:
                page.locator("button:has-text('Accetta')").click()
                print("✅ Cookie banner accettato")
                time.sleep(1)
            except:
                print("ℹ️ Nessun cookie banner da accettare")

            page.wait_for_load_state("networkidle")
            time.sleep(3)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("div.card-wrapper")
        print(f"🔎 Trovati {len(cards)} elementi con selector 'div.card-wrapper'\n")

        fg = FeedGenerator()
        fg.title("Comune di Castelgomberto - Novità")
        fg.link(href=url, rel="alternate")
        fg.description("Ultime notizie dal sito ufficiale del Comune di Castelgomberto")

        valid_count = 0
        titoli_visti = set()

        for i, card in enumerate(cards, start=1):
            print(f"📦 Card {i}")
            h3_tag = card.select_one("h3")
            a_tag = card.select_one("a[href]")

            if not a_tag or not h3_tag:
                print("❌ Nessun <a> o <h3> trovato → scarto\n")
                continue

            title = h3_tag.get_text(strip=True)
            if title.lower() in ["avvisi", "notizie", "comunicati"]:
                print(f"⏭️ Escluso: {title}\n")
                continue

            if title in titoli_visti:
                print("🔁 Titolo già visto, salto\n")
                continue
            titoli_visti.add(title)

            href = a_tag.get("href")
            if href.startswith("/home/novita"):
                href = href.replace("/home/novita", "")

            link = urljoin(base_url, href)

            print(f"🟢 Titolo: {title}")
            print(f"🔗 Link: {link}\n")

            pubdate = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
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
