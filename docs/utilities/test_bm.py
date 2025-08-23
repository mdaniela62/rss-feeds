# test_barbaranomossano.py
import os
from comuni import barbaranomossano

# Definisci il "sito" come nello sites_list.json
site = {
    "name": "Comune di Barbarano Mossano",
    "url": "https://www.comune.barbaranomossano.vi.it/home.html",
    "output": "feeds/barbaranomossano.xml"
}

try:
    xml = barbaranomossano.generate_feed(site)
    os.makedirs(os.path.dirname(site["output"]), exist_ok=True)
    with open(site["output"], "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"✅ Feed generato correttamente: {site['output']}")
except Exception as e:
    print(f"❌ Errore nello script {site['name']}")
    print("STDERR:", e)
