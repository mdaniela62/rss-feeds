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

    # Esempio formato: "Ult.agg. 28/05/2025"
    parts = date_str.replace("Ult.agg.", "").strip().split("/")
    if len(parts) == 3:
        giorno = int(parts[0])
        mese = int(parts[1])
        anno = int(parts[2])
        return datetime(anno, mese, giorno, tzinfo=timezone.utc)
    raise ValueError("Formato data non riconosciuto")


def generate_feed():
    print(" Inizio generazione feed per Comune di Malo")
    url = "http://www.comune.malo.vi.it/web/malo"
    #print(f" Richiesta pagina: {url}", flush=True)

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        #print(" Pagina caricata correttamente", flush=True)
    except Exception as e:
        print(f" Errore caricamento pagina: {e}", flush=True)
        return

    soup = BeautifulSoup(response.content, "lxml")

    fg = FeedGenerator()
    fg.title("Comune di Malo : Notizie")
    fg.link(href=url, rel="alternate")
    fg.description("Ultime notizie dal sito ufficiale del Comune di Malo")

    items = soup.select("div.contenutoSezioneNews")
    print(f" Elementi trovati: {len(items)}", flush=True)

    for idx, item in enumerate(items, start=1):
        title_tag = item.select_one("h3.underline a")
        link_tag = title_tag
        date_tag = item.select_one("span.noteNews")
        subtitle_tag = item.select_one("div.sottotitolo")

        if title_tag and link_tag:
            href = link_tag.get("href")
            if href and not href.startswith("http"):
                href = requests.compat.urljoin(url, href)

       #     print(f" Articolo: {title_tag.get_text(strip=True)} , {href}", flush=True)
            fe = fg.add_entry()
            fe.title(title_tag.get_text(strip=True))
            fe.link(href=href)
            fe.guid(href, permalink=True)

            description = subtitle_tag.get_text(strip=True) if subtitle_tag else title_tag.get_text(strip=True)
            fe.description(description)

            if date_tag:
                try:
                    pub_date = parse_italian_date(date_tag.get_text(strip=True))
                    fe.pubDate(format_datetime(pub_date))
                except Exception as e:
                    print(f"     Errore data '{date_tag.get_text(strip=True)}': {e}", flush=True)

    filename = "feeds/malo.xml"
    with open(filename, "wb") as f:
        f.write(fg.rss_str(pretty=True))

    print(f" Feed salvato in: {filename}", flush=True)


if __name__ == "__main__":
    generate_feed()
