
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import requests


def generate_feed():
    print("[INFO] Inizio generazione feed per Comune di Altissimo (Home)")

    try:
        response = requests.get("https://www.comune.altissimo.vi.it/home.html", timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        cards = soup.select("div.card-wrapper.border.border-light.rounded.shadow-sm")
        print(f" Trovati {len(cards)} elementi con struttura news")

        fg = FeedGenerator()
        fg.title("Comune di Altissimo - Home")
        fg.link(href="https://www.comune.altissimo.vi.it/home.html", rel="alternate")
        fg.description("Ultime notizie dal sito ufficiale del Comune di Altissimo")

        for card in cards:
            link_tag = card.select_one("a.text-decoration-none")
            title = link_tag.get_text(strip=True) if link_tag else ""
            link = link_tag["href"] if link_tag and "href" in link_tag.attrs else ""

            if not title or not link:
                continue

            if not link.startswith("http"):
                link = "https://www.comune.altissimo.vi.it" + link

            pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

            fe = fg.add_entry()
            fe.id(link)
            fe.title(title)
            fe.link(href=link)
            fe.pubDate(pub_date)

            print(f" Aggiunto: {title} - {link}")

        fg.rss_file("altissimo.xml")
        print(" Feed generato correttamente per Comune di Altissimo - altissimo.xml")

    except Exception as e:
        print(f" Errore feed Altissimo: {e}")


if __name__ == "__main__":
    generate_feed()
