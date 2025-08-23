import requests
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed

def generate_feed(site):
    url = site["url"]
    output_file = site["output"]

    # Scarica la pagina
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Crea il feed RSS
    feed = Rss201rev2Feed(
        title=site["name"],
        link=url,
        description=f"Feed RSS simulato per {site['name']}",
        language="it",
    )

    # Estrazione notizie (adatta alla struttura del sito di Barbarano Mossano)
    # Di solito le notizie sono in div con classe "news" o simile
    articles = soup.select("div.news-item, li.news, div.item, article")

    for art in articles:
        title = art.get_text(strip=True)
        link = art.find("a")["href"] if art.find("a") else url
        if link.startswith("/"):
            link = url.rstrip("/") + link
        feed.add_item(
            title=title,
            link=link,
            description=title,
        )

    # Ritorna la stringa XML
    return feed.writeString("utf-8")
