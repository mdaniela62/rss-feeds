import requests
from bs4 import BeautifulSoup

URL = "https://www.comune.schio.vi.it/Novita"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

try:
    response = requests.get(URL, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    articles = soup.select("div.card-teaser, div.card.card-teaser-image")

    print(f"Trovati {len(articles)} articoli.")
    print(soup.prettify()[:2000])  # Stampa i primi 2000 caratteri dell'HTML ricevuto

    for idx, article in enumerate(articles[:5], 1):
        title_tag = article.select_one("h3.card-title")
        title = title_tag.get_text(strip=True) if title_tag else "Senza titolo"
        print(f"{idx}. {title}")

except Exception as e:
    print("Errore durante la richiesta o il parsing:", e)
