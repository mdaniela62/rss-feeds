import requests
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
from datetime import datetime

def generate_feed(url, output_file):
    # Richiesta HTTP classica
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Feed di base
    feed = Rss201rev2Feed(
        title="Feed RSS simulato",
        link=url,
        description="Notizie generate automaticamente",
        language="it"
    )

    # 🔧 Adatta qui ai selettori reali del sito
    articles = soup.select("h3.card-title")
    for art in articles:
        a = art.find("a")
        if not a:
            continue

        title = a.get_text(strip=True)
        link = a["href"]
        # Se i link sono relativi:
        if link.startswith("/"):
            link = url.rstrip("/") + link

        # Data (se disponibile)
        date_tag = art.find_next("span", class_="data")
        pub_date = None
        if date_tag:
            try:
                pub_date = datetime.strptime(
                    date_tag.get_text(strip=True), "%A, %d %B %Y"
                )
            except Exception:
                pass

        # Descrizione opzionale
        description = ""

        feed.add_item(
            title=title,
            link=link,
            description=description,
            pubdate=pub_date
        )

    # Salvataggio feed
    with open(output_file, "w", encoding="utf-8") as f:
        feed.write(f, "utf-8")
