import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# URL della homepage del Comune di Schiavon
URL = "https://www.comune.schiavon.vi.it/"
TIMEOUT = 10

# Parole chiave da escludere (se necessario)
ESCLUDI_TITOLI = ["Servizi", "Albo Pretorio", "Numeri utili"]

print("➡️ Inizio generazione feed per Comune di Schiavon")

try:
    response = requests.get(URL, timeout=TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")

    # Selettore CSS per le notizie (da verificare con HTML reale)
    items = soup.select("div.card-wrapper")
    print(f"🔎 Trovati {len(items)} elementi con selector 'div.card-wrapper'")

    fg = FeedGenerator()
    fg.title("Comune di Schiavon - Novità")
    fg.link(href=URL, rel="alternate")
    fg.description("Ultime novità dal sito ufficiale del Comune di Schiavon")

    for item in items:
        link_tag = item.select_one("a.text-decoration-none")
        title_tag = item.select_one("h3")

        if not link_tag or not title_tag:
            continue

        title = title_tag.get_text(strip=True)

        # Filtra titoli non desiderati
        if any(keyword.lower() == title.lower() for keyword in ESCLUDI_TITOLI):
            print(f"⏭️ Escluso: {title}")
            continue

        link = link_tag.get("href")
        if not link.startswith("http"):
            link = "https://www.comune.schiavon.vi.it" + link

        pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        fe = fg.add_entry()
        fe.id(link)
        fe.title(title)
        fe.link(href=link)
        fe.pubDate(pub_date)

        print(f"✅ Aggiunto articolo: {title} → {link}")

    fg.rss_file("feed_schiavon.xml")
    print("✅ Feed generato correttamente per Comune di Schiavon")

except Exception as e:
    print(f"❌ Errore durante la generazione del feed per Comune di Schiavon: {e}")
