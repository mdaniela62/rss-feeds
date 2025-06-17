import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from email.utils import format_datetime


def parse_italian_date(date_str):
    mesi = {
        "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
        "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12
    }
    parts = date_str.strip().split()
    if len(parts) == 3:
        giorno = int(parts[0])
        mese = mesi.get(parts[1].lower(), 0)
        anno = int(parts[2])
        return datetime(anno, mese, giorno, tzinfo=timezone.utc)
    raise ValueError("Formato data non riconosciuto")


def genera_feed():
    url = "https://www.comune.altissimo.vi.it/home/novita.html"
    print(f"🔎 Richiesta pagina: {url}", flush=True)

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        print("✅ Pagina caricata correttamente", flush=True)
    except Exception as e:
        print(f"❌ Errore caricamento pagina: {e}", flush=True)
        return

    soup = BeautifulSoup(response.content, "lxml")

    fg = FeedGenerator()
    fg.title("Comune di Altissimo - Novità")
    fg.link(href=url, rel="alternate")
    fg.description("Ultime novità dal sito ufficiale del Comune di Altissimo")

    selectors = [
        "div.card-wrapper.border.border-light.rounded.shadow-sm.cmp-list-card-img.cmp-list-card-img-hr"
    ]

    total_items = 0

    for selector in selectors:
        items = soup.select(selector)
        print(f"📄 Elementi trovati con selector '{selector}': {len(items)}", flush=True)
        total_items += len(items)

        for idx, item in enumerate(items, start=1):
            title_tag = item.select_one("h3.cmp-list-card-img__body-title a")
            link_tag = title_tag
            date_tag = item.select_one("span.data")
            summary_tag = item.select_one("p.card-text")

            if title_tag and link_tag:
                href = link_tag.get("href")
                if href and not href.startswith("http"):
                    href = requests.compat.urljoin(url, href)

                print(f"  ✅ Articolo: {title_tag.get_text(strip=True)} → {href}", flush=True)
                fe = fg.add_entry()
                fe.title(title_tag.get_text(strip=True))
                fe.link(href=href)
                fe.guid(href, permalink=True)

                if summary_tag:
                    fe.description(summary_tag.get_text(strip=True))
                else:
                    fe.description(title_tag.get_text(strip=True))

                if date_tag:
                    try:
                        pub_date = parse_italian_date(date_tag.get_text(strip=True))
                        fe.pubDate(format_datetime(pub_date))
                    except Exception as e:
                        print(f"    ⚠️ Errore data '{date_tag.get_text(strip=True)}': {e}", flush=True)

    print(f"🔔 Totale articoli trovati: {total_items}", flush=True)

    filename = "feed_altissimo.xml"
    with open(filename, "wb") as f:
        f.write(fg.rss_str(pretty=True))

    print(f"💾 Feed salvato in: {filename}", flush=True)


if __name__ == "__main__":
    genera_feed()
