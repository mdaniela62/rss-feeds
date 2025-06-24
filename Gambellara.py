import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

def genera_feed(nome_comune, url_base, url, selector, base_href):
    print(f"➡️ Inizio generazione feed per {nome_comune}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        items = soup.select(selector)
        print(f"🔎 Trovati {len(items)} elementi con selector '{selector}'")

        fg = FeedGenerator()
        fg.title(f"{nome_comune} - Novità")
        fg.link(href=url_base, rel="alternate")
        fg.description(f"Ultime novità dal sito ufficiale del {nome_comune}")

        for item in items:
            link_tag = item.select_one("a")
            title_tag = item.select_one("a")

            if not link_tag or not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = link_tag.get("href")
            if not link.startswith("http"):
                link = base_href + link

            pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.pubDate(pub_date)

            print(f"✅ Aggiunto articolo: {title} → {link}")

        filename = f"feed_{nome_comune.lower().replace(' ', '_')}.xml"
        fg.rss_file(filename)
        print(f"✅ Feed generato correttamente per {nome_comune} → {filename}")

    except Exception as e:
        print(f"❌ Errore durante la generazione del feed per {nome_comune}: {e}")



# Comune di Gambellara
genera_feed(
    nome_comune="Comune di Gambellara",
    url_base="https://www.comune.gambellara.vi.it/home/novita",
    url="https://www.comune.gambellara.vi.it/home/novita",
    selector="div.cmp-list-card-img__body",
    base_href="https://www.comune.gambellara.vi.it"
)

