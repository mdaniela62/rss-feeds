import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# URL della home del Comune di Barbarano Mossano
URL = "https://www.comune.barbaranomossano.vi.it/home.html"

TIMEOUT = 10
def generate_feed():
     print(" Inizio generazione feed per Comune di Barbarano Mossano")

try:
    response = requests.get(URL, timeout=TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")

    # Selettore CSS per le notizie
    items = soup.select("div.card-wrapper")
    print(f" Trovati {len(items)} elementi con selector 'div.card-wrapper'")

    fg = FeedGenerator()
    fg.title("Comune di Barbarano Mossano - Novità")
    fg.link(href=URL, rel="alternate")
    fg.description("Ultime novità dal sito ufficiale del Comune di Barbarano Mossano")

    for item in items:
        link_tag = item.select_one("a.text-decoration-none")
        title_tag = item.select_one("h3")

        if not link_tag or not title_tag:
            continue

        link = link_tag.get("href")
        if not link.startswith("http"):
            link = "https://www.comune.barbaranomossano.vi.it" + link

        title = title_tag.get_text(strip=True)
        pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        fe = fg.add_entry()
        fe.id(link)
        fe.title(title)
        fe.link(href=link)
        fe.pubDate(pub_date)

        print(f" Aggiunto articolo: {title} : {link}")

    fg.rss_file("feeds/barbarano.xml")
    print(" Feed generato correttamente per Comune di Barbarano Mossano")

except Exception as e:
    print(f" Errore durante la generazione del feed per Comune di Barbarano Mossano: {e}")

if __name__ == "__main__":
    generate_feed()
