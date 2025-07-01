from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import requests

def genera_feed_schio():
    print("\n➡️ Inizio generazione feed per Comune di Schio")

    try:
        url = "https://www.comune.schio.vi.it/home/novita.html"
        base_url = "https://www.comune.schio.vi.it"
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        items = soup.select("div.cmp-list-card-img__body")
        print(f"🔎 Trovati {len(items)} elementi con selector 'div.cmp-list-card-img__body'")

        fg = FeedGenerator()
        fg.title("Comune di Schio - Novità")
        fg.link(href=url, rel="alternate")
        fg.description("Ultime notizie dal sito ufficiale del Comune di Schio")

        for item in items:
            link_tag = item.select_one("a[data-element='news-link']")
            title = link_tag.get_text(strip=True) if link_tag else None
            link = link_tag.get("href") if link_tag else None

            if not title or not link:
                continue

            if not link.startswith("http"):
                link = base_url + link

            pubdate = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.pubDate(pubdate)

            print(f"✅ Aggiunto: {title} → {link}")

        fg.rss_file("schio.xml")
        print("✅ Feed generato → schio.xml")

    except Exception as e:
        print(f"❌ Errore feed Schio: {e}")

if __name__ == "__main__":
    genera_feed_schio()
