import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# URL corretta della home page del Comune di Velo d'Astico
URL = "https://www.comune.velodastico.vi.it/"
TIMEOUT = 10

print("➡️ Inizio generazione feed per Comune di Velo d'Astico (da Home)")

try:
    response = requests.get(URL, timeout=TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")

    # Selettore CSS corretto per le notizie nella home page
    items = soup.select("div.data-object_id")
    print(f"🔎 Trovati {len(items)} elementi con selector 'div.data-object_id'")

    fg = FeedGenerator()
    fg.title("Comune di Velo d'Astico - Novità (Home)")
    fg.link(href=URL, rel="alternate")
    fg.description("Ultime novità dal sito ufficiale del Comune di Velo d'Astico (Home)")

    for item in items:
        link_tag = item.select_one("h3 a")
        title_tag = item.select_one("h3 a")

        if not link_tag or not title_tag:
            continue

        title = title_tag.get_text(strip=True)

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

    fg.rss_file("feed_velo_home.xml")
    print("✅ Feed generato correttamente per Comune di Velo d'Astico (Home)")

except Exception as e:
    print(f"❌ Errore durante la generazione del feed per Comune di Velo d'Astico (Home): {e}")
