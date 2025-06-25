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

        # DEBUG: salva la pagina HTML per ispezione locale
        with open(f"debug_{nome_comune.lower().replace(' ', '_')}.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        items = soup.select(selector)
        if not items:
            print(f"⚠️ Nessun elemento trovato con '{selector}', provo fallback su tutti i tag <a>")
            items = soup.find_all("a")

        print(f"🔎 Trovati {len(items)} elementi per {nome_comune}")

        fg = FeedGenerator()
        fg.title(f"{nome_comune} - Novità")
        fg.link(href=url_base, rel="alternate")
        fg.description(f"Ultime novità dal sito ufficiale del {nome_comune}")

        for item in items:
            title = item.get_text(strip=True)
            link = item.get("href")
            if not title or not link or link.startswith("#"):
                continue

            if not link.startswith("http"):
                link = base_href.rstrip("/") + link

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


