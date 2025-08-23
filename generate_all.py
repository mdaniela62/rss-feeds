import json
import subprocess
# debug #
##import os, sys
#print("Working dir:", os.getcwd())
#print("Sys.path:", sys.path)
#print("Files in comuni/:", os.listdir("comuni"))
#fine debug#

# Carica la lista dei siti
with open("sites_list.json", "r", encoding="utf-8") as f:
    sites = json.load(f)

# Cicla sui siti e genera i feed
for site in sites:
    script_name = site.get("script")
    if not script_name:
        print(f"❌ Errore: manca la chiave 'script' per il sito {site.get('name', 'sconosciuto')}")
        continue

    print(f"🚀 Generating feed for: {script_name}")
    result = subprocess.run(
        ["python", "generate_rss.py", script_name],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("⚠️ Error output:", result.stderr)

