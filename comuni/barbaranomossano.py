import requests
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
from urllib.parse import urljoin

def generate_feed(site):
    print(" Inizio generazione feed per Comune di Barbarano Mossano")
    url = site["url"]

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

    # Estrazione notizie (layout vari Kibernetes + fallback)
    containers = soup.select(
        #"div.card-wrapper, div.card.card-teaser, li.card-teaser, "
        #"article, div.news-item, li.news, div.item"

        "div.card-wrapper"
          )

    for c in containers:
        #a = c.select_one("h3.card-title a") or c.select_one("a.read-more") or c.find("a")
        a = c.select_one("h3.card-title a") or c.find("a")
        if not a or not a.get("href"):
            continue

        title = a.get_text(strip=True) or "Senza titolo"
        if title.lower() in ["servizi", "vai al contenuto"]:
                print(f" Escluso: {title}\n")
                continue



        link = urljoin(url, a["href"])

        desc_el = c.select_one(".card-text, .description, p")
        description = (desc_el.get_text(strip=True) if desc_el else title)

        feed.add_item(
            title=title,
            link=link,
            description=description,
        )

    # ✅ ritorna la stringa XML del feed
    return feed.writeString("utf-8")


# Compatibilità se eseguito da solo
if __name__ == "__main__":
    fake_site = {
        "name": "Comune di Barbarano Mossano",
        "url": "https://www.comune.barbaranomossano.vi.it/home.html",
        "output": "feeds/barbaranomossano.xml"
    }
    xml = generate_feed(fake_site)
    with open(fake_site["output"], "w", encoding="utf-8") as f:
        f.write(xml)
    print("[OK] Feed RSS per Barbarano Mossano generato.")
