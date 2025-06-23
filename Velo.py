import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# URL della pagina Novità del Comune di Velo d'Astico
URL = "https://www.comune.velodastico.vi.it/Novita"
TIMEOUT = 10

# Parole chiave da escludere (titoli generici)
ESCLUDI_TITOLI = ["Comunicati", "Notizie", "Avvisi"]

print("➡️ Inizio generazione feed per Comune di Velo d'Astico")

try:
    response = requests.get(URL, timeout=TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")

    # Selettore CSS corretto per le notizie
    items = soup.select("div.card.cmp-list-card-img")
    print(f"🔎 Trovati {len(items)} elementi con selector 'div.card.cmp-list-card-img'")

    fg = FeedGenerator()
    fg.title("Comune di Velo d'Astico - Novità")
    fg.link(href=URL, rel="alternate")
    fg.description("Ultime novità dal sito ufficiale del Comune di Velo d'Astico")

    for item in items:
        link_tag = item.select_one("h3 a")
        title_tag = item.select_one("h3 a")

        if not link_tag or not title_tag:
            continue

        title = title_tag.get_text(strip=True)

        # Filtra titoli non desiderati
        if any(keyword.lower() == title.lower() for keyword in ESCLUDI_TITOLI):
            print(f"⏭️ Escluso: {title}")
            continue

        link = link_tag.get("href")
        if not link.startswith("http"):
            link = "https://www.comune.velodastico.vi.it" + link

        pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        fe = fg.add_entry()
        fe.id(link)
        fe.title(title)
        fe.link(href=link)
        fe.pubDate(pub_date)

        print(f"✅ Aggiunto articolo: {title} → {link}")

    fg.rss_file("feed_velo.xml")
    print("✅ Feed generato correttamente per Comune di Velo d'Astico")

except Exception as e:
    print(f"❌ Errore durante la generazione del feed per Comune di Velo d'Astico: {e}")
