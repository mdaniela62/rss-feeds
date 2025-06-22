import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# URL della pagina Novità del Comune di Velodastico
URL = "https://www.comune.velodastico.vi.it/Novita"
TIMEOUT = 10

# Parole chiave da escludere (titoli generici)
ESCLUDI_TITOLI = ["Comunicati", "Notizie", "Avvisi"]

print("➡️ Inizio generazione feed per Comune di Velodastico")

try:
    response = requests.get(URL, timeout=TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")

    # Utilizzo tag h3 per ricerca notizie
    items = soup.find_all("h3")
    print(f"🔎 Trovati {len(items)} elementi <h3>")

    fg = FeedGenerator()
    fg.title("Novità / Homepage - Comune di Velo d'Astico")
    fg.link(href=URL, rel="alternate")
    fg.description("Avvisi, comunicati stampa e notizie più importanti sempre aggiornate, della città")

    for h3 in items:
        title = h3.get_text(strip=True)

        # Filtra titoli non desiderati
        if any(keyword.lower() == title.lower() for keyword in ESCLUDI_TITOLI):
            print(f"⏭️ Escluso: {title}")
            continue

        link_tag = h3.find("a")
        if not link_tag or not link_tag.get("href"):
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

    fg.rss_file("feed_velodastico.xml")
    print("✅ Feed generato correttamente per Comune di Velodastico")

except Exception as e:
    print(f"❌ Errore durante la generazione del feed per Comune di Velodastico: {e}")
