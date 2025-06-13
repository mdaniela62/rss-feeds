import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Lista dei siti da processare
sites = [
    {
        "name": "Comune di Altissimo",
        "url": "https://www.comune.altissimo.vi.it/home/novita.html",
        "rss_file": "altissimo.xml",
        "item_selector": "div.list-item",
        "title_selector": "h2.list-title",
        "link_selector": "a",
        "date_selector": "div.list-date"
    },
    {
        "name": "Comune di Arzignano",
        "url": "https://www.comune.arzignano.vi.it/home/novita.html",
        "rss_file": "arzignano.xml",
        "item_selector": "div.card-wrapper",
        "title_selector": "h3.cmp-list-card-img__body-title a",
        "link_selector": "h3.cmp-list-card-img__body-title a",
        "date_selector": "span.data"
    }
]

# Funzione per generare il feed RSS con logging

def generate_feed(site):
    try:
        print(f"\n➡️ Inizio generazione feed per: {site['name']}")
        response = requests.get(site["url"], timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        fg = FeedGenerator()
        fg.title(site["name"] + " - Novità")
        fg.link(href=site["url"], rel="alternate")
        fg.description(f"Ultime novità dal sito ufficiale del {site['name']}")

        items = soup.select(site["item_selector"])
        print(f"🔎 Trovati {len(items)} elementi con selector '{site['item_selector']}'")

        for idx, item in enumerate(items, start=1):
            title_tag = item.select_one(site["title_selector"])
            link_tag = item.select_one(site["link_selector"])
            date_tag = item.select_one(site["date_selector"])

            if title_tag and link_tag:
                href = link_tag.get("href")
                if href and not href.startswith("http"):
                    href = requests.compat.urljoin(site["url"], href)

                print(f"  ✅ Articolo {idx}: {title_tag.get_text(strip=True)} → {href}")
                fe = fg.add_entry()
                fe.title(title_tag.get_text(strip=True))
                fe.link(href=href)
                if date_tag:
                    fe.published(date_tag.get_text(strip=True))

        fg.rss_file(site["rss_file"])
        print(f"✅ Feed generato correttamente per {site['name']}")

    except Exception as e:
        print(f"❌ Errore durante la generazione del feed per {site['name']}: {e}")


# Genera i feed per tutti i siti in lista
for site in sites:
    generate_feed(site)

print("\n🚀 Elaborazione completata.")
