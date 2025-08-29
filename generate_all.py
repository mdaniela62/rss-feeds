import json
from generate_rss import main

with open("sites_list.json", "r", encoding="utf-8") as f:
    sites = json.load(f)

for site in sites:
    print(f"🚀 Generating feed for: {site.get('name', site.get('script'))}")
    # passo l'intero dict: generate_rss.main lo gestisce correttamente
    main(site)
