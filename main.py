from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from email.utils import format_datetime
import sys

app = Flask(__name__)

def parse_italian_date(date_str):
    mesi = {
        "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
        "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12
    }
    parts = date_str.strip().split()
    if len(parts) == 3:
        giorno = int(parts[0])
        mese = mesi.get(parts[1].lower(), 0)
        anno = int(parts[2])
        return datetime(anno, mese, giorno, tzinfo=timezone.utc)
    raise ValueError("Formato data non riconosciuto")

@app.route("/")
def index():
    return "Feed RSS disponibile su /rss"

@app.route("/rss")
def rss():
    fg = FeedGenerator()
    fg.title("Feed di Test Comune di Arzignano")
    fg.link(href="https://www.comune.arzignano.vi.it/", rel="alternate")
    fg.description("Feed di test generato tramite Render")

    # Articolo di test
    fe = fg.add_entry()
    fe.title("Articolo di test")
    fe.link(href="https://www.comune.arzignano.vi.it/test")
    fe.guid("https://www.comune.arzignano.vi.it/test", permalink=True)
    fe.description("Descrizione di test generato automaticamente.")
    fe.pubDate(format_datetime(datetime.now(timezone.utc)))

    rss_feed = fg.rss_str(pretty=True)
    return Response(rss_feed, mimetype="application/rss+xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
