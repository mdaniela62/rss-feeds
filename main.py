import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# URL della pagina novità del Comune di Arzignano
URL = "https://www.comune.arzignano.vi.it/home/novita.html"

# Recupera la pagina
response = requests.get(URL)
response.raise_for_status()

soup = BeautifulSoup(response.content, "lxml")

# Generazione feed
fg = FeedGenerator()
fg.title("Comune di Arzignano - Novità")
fg.link(href=URL, rel='alternate')
fg.description("Ultime novità dal sito ufficiale del Comune di Arzignano")
fg.language('it')

# Trova le notizie
news_items = soup.select("div.news li a")

for item in news_items:
    title = item.get_text(strip=True)
    link = item['href']
    if not link.startswith('http'):
        link = "https://www.comune.arzignano.vi.it" + link

    fe = fg.add_entry()
    fe.title(title)
    fe.link(href=link)
    fe.pubDate(datetime.utcnow())  # Non c'è data nel sito ➔ mettiamo data attuale

# Salva il feed RSS in un file XML
fg.rss_file("arzignano.xml")
