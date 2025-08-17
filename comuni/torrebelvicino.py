# Torrebelvicino_Playwright.py
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
import time

def generate_feed():
    print(" Inizio generazione feed per Comune di Torrebelvicino (da /home)")

    try:
        url = "https://www.comune.torrebelvicino.vi.it/"
        base_url = "https://www.comune.torrebelvicino.vi.it"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True,
                                        args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            page = context.new_page()
            page.goto(url, timeout=60000)

            try:
                page.locator("button:has-text('Accetta')").click()
                print(" Cookie banner accettato")
                time.sleep(1)
            except:
                print(" Nessun cookie banner da accettare")

            page.wait_for_load_state("networkidle")
            time.sleep(3)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("div.card-wrapper")
        print(f" Trovati {len(cards)} elementi con selector 'div.card-wrapper'\n")

        fg = FeedGenerator()
        fg.title("Comune di Torrebelvicino - Novità")
        fg.link(href=url, rel="alternate")
        fg.description("Ultime notizie dalla home page del Comune di Torrebelvicino")

        valid_count = 0
        titoli_visti = set()

        for i, card in enumerate(cards, start=1):
            print(f" Card {i}")
            h3_tag = card.select_one("h3")
            a_tag = card.select_one("a[href]")

            if not a_tag or not h3_tag:
                print(" Nessun <a> o <h3> trovato → scarto\n")
                continue

            title = h3_tag.get_text(strip=True)
            if title.lower() in ["avvisi", "notizie", "comunicati"]:
                print(f" Escluso: {title}\n")
                continue

            if title in titoli_visti:
                print(" Titolo già visto, salto\n")
                continue
            titoli_visti.add(title)

            href = a_tag.get("href")
            link = urljoin(base_url, href)

            print(f" Titolo: {title}")
            print(f" Link: {link}\n")

            pubdate = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.pubDate(pubdate)

            valid_count += 1

        if valid_count > 0:
            fg.rss_file("torrebelvicino.xml")
            print(f" Feed generato : torrebelvicino.xml con {valid_count} articoli")
        else:
            print(" Nessun elemento valido trovato per il feed.")

    except Exception as e:
        print(f" Errore feed Torrebelvicino: {e}")

if __name__ == "__main__":
    generate_feed()
