from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import feedgenerator
from datetime import datetime
import re

BASE_URL = "https://www.comune.posina.vi.it"
NEWS_URL = BASE_URL + "/Novita"

MONTHS_IT = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
    "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12
}

def _parse_date_it(s: str) -> datetime:
    """
    Accetta stringhe tipo 'Mercoledì, 13 Agosto 2025' o simili.
    Se fallisce, torna 'oggi' (meglio un valore che niente).
    """
    if not s:
        return datetime.utcnow()
    s = re.sub(r"\s+", " ", s.strip())
    # estrai '13 Agosto 2025'
    m = re.search(r"(\d{1,2})\s+([A-Za-zÀ-ÿ]+)\s+(\d{4})", s)
    if not m:
        return datetime.utcnow()
    day = int(m.group(1))
    month_name = m.group(2).lower()
    month = MONTHS_IT.get(month_name, None)
    year = int(m.group(3))
    if not month:
        return datetime.utcnow()
    try:
        return datetime(year, month, day)
    except Exception:
        return datetime.utcnow()

def _fetch_html_with_playwright(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        # aspetta che le card siano presenti (selettore prudente)
        try:
            page.wait_for_selector("h3.card-title a", timeout=15000)
        except Exception:
            # fallback: almeno attendi il networkidle
            page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()
    return html

def _extract_items(html: str):
    soup = BeautifulSoup(html, "html.parser")
    items = []

    for h3 in soup.select("h3.card-title"):
        a = h3.find("a")
        if not a:
            continue
        title = a.get_text(strip=True)
        link = urljoin(BASE_URL, a.get("href", "").strip())

        # data: il primo span.data successivo
        date_span = h3.find_next("span", class_="data")
        pubdate = _parse_date_it(date_span.get_text(strip=True) if date_span else "")

        # descrizione: prova a prendere un paragrafo vicino (card-text o p dopo h3)
        desc = ""
        # cerca un paragrafo entro lo stesso blocco card, se esiste
        card = h3.find_parent(class_=re.compile(r"\bcard\b")) or h3.parent
        if card:
            # prima un div.card-text, poi un p generico
            cand = card.select_one(".card-text") or card.find("p")
            if cand:
                desc = cand.get_text(" ", strip=True)
        if not desc:
            # fallback: il paragrafo subito dopo l'h3
            sib_p = h3.find_next("p")
            if sib_p:
                # evita di saltare nella card successiva
                # fermati se arriva prima di un altro h3.card-title
                next_h3 = h3.find_next("h3", class_="card-title")
                if not next_h3 or (sib_p and sib_p.sourcepos < next_h3.sourcepos if hasattr(sib_p, "sourcepos") else True):
                    desc = sib_p.get_text(" ", strip=True)

        items.append({
            "title": title,
            "link": link,
            "pubdate": pubdate,
            "description": desc or ""
        })

    return items

def generate_feed(site: dict | None = None) -> str:
    """
    Firma compatibile con generate_rss.py: accetta opzionalmente 'site',
    ma non è obbligatorio.
    """
    url = (site or {}).get("url") or NEWS_URL
    html = _fetch_html_with_playwright(url)
    entries = _extract_items(html)

    feed = feedgenerator.Rss201rev2Feed(
        title="Comune di Posina - Novità",
        link=url,
        description="Notizie dal sito ufficiale del Comune di Posina",
        language="it",
    )

    for e in entries:
        feed.add_item(
            title=e["title"],
            link=e["link"],
            description=e["description"],
            pubdate=e["pubdate"],
        )

    return feed.writeString("utf-8")

# Fallback usato da generate_rss.py se manca generate_feed()
def scrape_posina(site: dict | None = None) -> str:
    return generate_feed(site)

if __name__ == "__main__":
    xml = generate_feed()
    with open("posina.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    print("[OK] Feed RSS per Posina generato.")
