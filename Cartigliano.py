import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# Configurazione Feed Cartigliano
URL = "https://www.comune.cartigliano.vi.it/"
TIMEOUT = 10

print("➡️ Inizio generazione feed per Comune di Cartigliano")

try:
    resp = requests.get(URL, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "lxml")

    # Individua i blocchi di Notizie
    block = soup.find(lambda t: t.name=="h2" and "Notizie" in t.get_text())
    items = block.find_next_siblings("h3") if block else []
    print(f"🔎 Trovati {len(items)} notizie nella sezione 'Notizie'")

    fg = FeedGenerator()
    fg.title("Comune di Cartigliano - Notizie")
    fg.link(href=URL, rel="alternate")
    fg.description("Novità dal sito ufficiale del Comune di Cartigliano")

    for h3 in items:
        title = h3.get_text(strip=True)
        sib = h3.find_next_sibling(text=lambda t: t and any(x in t for x in ["Notizia","Avviso","Avvisa"]))
        date_txt = sib.strip().split(maxsplit=2)[-2:] if sib else []
        date_str = " ".join(date_txt)
        try:
            pub = datetime.strptime(date_str, "%d %b %Y")
            pub_date = pub.strftime("%a, %d %b %Y %H:%M:%S GMT")
        except:
            pub_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        link_tag = h3.find("a")
        link = URL.rstrip("/") + link_tag["href"] if link_tag else URL
        fe = fg.add_entry()
        fe.id(link); fe.title(title); fe.link(href=link); fe.pubDate(pub_date)
        print(f"✅ Aggiunto: {title} – {pub_date}")

    fg.rss_file("cartigliano.xml")
    print("✅ Feed cartigliano.xml creato con successo")

except Exception as e:
    print("❌ Errore feed Cartigliano:", e)
