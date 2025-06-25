""
# Nuovo script Playwright per Gambellara (usa GitHub Actions, salvataggio su GitHub)

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import os
import subprocess

def genera_feed_gambellara():
    print("➡️ Inizio generazione feed per Comune di Gambellara (con Playwright)")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.comune.gambellara.vi.it/home/novita", timeout=20000)
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

        # Commit automatico su GitHub
        subprocess.run(["git", "config", "--global", "user.name", "github-actions"])
        subprocess.run(["git", "config", "--global", "user.email", "github-actions@github.com"])
        subprocess.run(["git", "add", "feed_gambellara.xml"])
        subprocess.run(["git", "commit", "-m", "Aggiornamento automatico feed Gambellara"])
        subprocess.run(["git", "push"])

    except Exception as e:
        print(f"❌ Errore durante la generazione del feed per Comune di Gambellara: {e}")

if __name__ == "__main__":
    genera_feed_gambellara()
