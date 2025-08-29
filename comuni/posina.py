from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import feedgenerator
import os
from datetime import datetime, timezone
import re

BASE_URL = "https://www.comune.posina.vi.it"
NEWS_URL = BASE_URL + "/Novita"

MONTHS_IT = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
    "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12
}

def _parse_date_it(s: str) -> datetime:
    """Accetta stringhe tipo 'Mercoledì, 13 Agosto 2025' e ritorna datetime UTC."""
    if not s:
        return datetime.now(timezone.utc)
    s = re.sub(r"\s+", " ", s.strip())
    m = re.search(r"(\d{1,2})\s+([A-Za-zÀ-ÿ]+)\s+(\d{4})", s)
    if not m:
        return datetime.now(timezone.utc)
    day = int(m.group(1))
    month_name = m.group(2).lower()
    month = MONTHS_IT.get(month_name, None)
    year = int(m.group(3))
    if not month:
        return datetime.now(timezone.utc)
    try:
        return datetime(year, month, day, tzinfo=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)

def _fetch_html_with_playwright(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        try:
            page.wait_for_selector("h3.card-title a", timeout=15000)
        except Exception:
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

        date_span = h3.find_next("span", class_="data")
        pubdate = _parse_date_it(date_span.get_text(strip=True) if date_span else "")

        desc = ""
        card = h3.find_parent(class_=re.compile(r"\bcard\b")) or h3.parent
        if card:
            cand = card.select_one(".card-text") or card.find("p")
            if cand:
                desc = cand.get_text(" ", strip=True)
        if not desc:
            sib_p = h3.find_next("p")
            if sib_p:
                next_h3 = h3.find_next("h3", class_="card-title")
                if not next_h3 or True:
                    desc = sib_p.get_text(" ", strip=True)

        items.append({
            "title": title,
            "link": link,
            "pubdate": pubdate,
            "description": desc or ""
        })

    return items

def generate_feed(site: dict | None = None) -> str:
    """Genera il feed RSS per il Comune di Posina e ritorna il contenuto XML."""
    print("Inizio generazione feed per Comune di Posina")
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

    # Percorso di output
    output_path = (site or {}).get("output", "feeds/posina.xml")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Salvataggio XML
    xml_content = feed.writeString("utf-8")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    print(f"[OK] Feed generato: {output_path}")
    return xml_content

# Fallback usato da generate_rss.py
def scrape_posina(site: dict | None = None) -> str:
    return generate_feed(site)

if __name__ == "__main__":
    generate_feed()
