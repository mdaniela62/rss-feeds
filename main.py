import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
from datetime import datetime

BASE_URL = "https://www.comune.altissimo.vi.it/home/novita.html"


def fetch_articles():
    response = requests.get(BASE_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    items = []

    for link in soup.select(".elenco_novita .media-body a"):
        title = link.get_text(strip=True)
        url = urljoin(BASE_URL, link.get("href"))
        items.append({"title": title, "url": url})

    return items


def generate_feed(items):
    fg = FeedGenerator()
    fg.title("Comune di Altissimo - Novità")
    fg.link(href=BASE_URL, rel='alternate')
    fg.description("Ultime novità dal sito ufficiale del Comune di Altissimo")

    pubdate = datetime.utcnow()

    for item in items:
        fe = fg.add_entry()
        fe.title(item['title'])
        fe.link(href=item['url'])
        fe.pubDate(pubdate)

    return fg.rss_str(pretty=True)


if __name__ == "__main__":
    articles = fetch_articles()
    rss_feed = generate_feed(articles)

    with open("altissimo.xml", "wb") as f:
        f.write(rss_feed)
