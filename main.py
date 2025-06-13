import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Configurazione dei siti da monitorare
SITES = [
    {
        "name": "Comune di Altissimo",
        "url": "https://www.comune.altissimo.vi.it/home/novita.html",
        "rss_file": "altissimo.xml",
    },
    {
        "name": "Comune di Arzignano",
        "url": "https://www.comune.arzignano.vi.it/home/novita.html",
        "rss_file": "arzignano.xml",
    }
]

def extract_articles(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")

    items = []

    for link in soup.select(".elenco-novita .media-body a"):
        title = link.get_text(strip=True)
        href = link.get("href")
        if href and not href.startswith("http"):
            href = requests.compat.urljoin(url, href)
        items.append({"title": title, "link": href})

    return items


def generate_feed(site_name, site_url, articles, output_file):
    fg = FeedGenerator()
    fg.title(f"{site_name} - Novità")
    fg.link(href=site_url, rel="alternate")
    fg.description(f"Ultime novità dal sito ufficiale del {site_name}")

    for article in articles:
        fe = fg.add_entry()
        fe.title(article["title"])
        fe.link(href=article["link"])

    fg.rss_file(output_file)


def main():
    for site in SITES:
        print(f"Generazione feed per: {site['name']}")
        articles = extract_articles(site["url"])
        generate_feed(site["name"], site["url"], articles, site["rss_file"])


if __name__ == "__main__":
    main()
