# Script Playwright per Gambellara (debug avanzato con browser visibile e user-agent personalizzato)

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import os
import subprocess

def genera_feed_gambellara():
    print("\n➡️ Inizio generazione feed per Comune di Gambellara (Playwright visibile + user-agent)")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Browser visibile
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
            page = context.new_page()
            page.goto("https://www.comune.gambellara.vi.it/home/novita", timeout=20000)
            page.wait_for_timeout(3000)
            content = page.content()
            browser.close()
            
        soup = BeautifulSoup(content, "lxml")
        items = soup.select("div.cmp-list-card-img__body")
        print(f"🔎 Trovati {len(items)} elementi con selector 'div.cmp-list-card-img__body'")

        fg = FeedGenerator()
        fg.title("Comune di Gambellara - Novità")
        fg.link(href="https://www.comune.gambellara.vi.it/home/novita", rel="alternate")
        fg.description("Ultime novità dal sito ufficiale del Comune di Gambellara")

        for item in items:
            a_tag = item.select_one("a")
            title = a_tag.get_text(strip=True) if a_tag else ""
            link = a_tag.get("href") if a_tag else None

            if not title or not link:
                continue

            if not link.startswith("http"):
                link = "https://www.comune.gambellara.vi.it" + link

            pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.pubDate(pub_date)

            print(f"✅ Aggiunto articolo: {title} → {link}")

        fg.rss_file("feed_gambellara.xml")
        print("✅ Feed generato correttamente per Comune di Gambellara → feed_gambellara.xml")

        # ❌ Commit disabilitato per evitare violazioni da esecuzione automatica
        # subprocess.run(["git", "config", "--global", "user.name", "github-actions"])
        # subprocess.run(["git", "config", "--global", "user.email", "github-actions@github.com"])
        # subprocess.run(["git", "add", "feed_gambellara.xml"])
        # subprocess.run(["git", "commit", "-m", "Aggiornamento automatico feed Gambellara"])
        # subprocess.run(["git", "push"])

    except Exception as e:
        print(f"❌ Errore durante la generazione del feed per Comune di Gambellara: {e}")

if __name__ == "__main__":
    genera_feed_gambellara()


# Script Altissimo da home page (versione aggiornata)

def genera_feed_altissimo():
    print("\n➡️ Inizio generazione feed per Comune di Altissimo (Home)")

    try:
        response = requests.get("https://www.comune.altissimo.vi.it/home.html", timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        cards = soup.select("div.card-wrapper.border.border-light.rounded.shadow-sm")
        print(f"🔎 Trovati {len(cards)} elementi con struttura news")

        fg = FeedGenerator()
        fg.title("Comune di Altissimo - Home")
        fg.link(href="https://www.comune.altissimo.vi.it/home.html", rel="alternate")
        fg.description("Ultime notizie dal sito ufficiale del Comune di Altissimo")

        for card in cards:
            link_tag = card.select_one("a.text-decoration-none")
            title = link_tag.get_text(strip=True) if link_tag else ""
            link = link_tag["href"] if link_tag and "href" in link_tag.attrs else ""

            if not title or not link:
                continue

            if not link.startswith("http"):
                link = "https://www.comune.altissimo.vi.it" + link

            pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.pubDate(pub_date)

            print(f"✅ Aggiunto: {title} → {link}")

        fg.rss_file("altissimo.xml")
        print("✅ Feed generato correttamente per Comune di Altissimo → altissimo.xml")

    except Exception as e:
        print(f"❌ Errore feed Altissimo: {e}")

# Esecuzione principale per entrambi i feed
if __name__ == "__main__":
    genera_feed_gambellara()
    genera_feed_altissimo()
