import json
import subprocess

with open("sites_list.json", "r", encoding="utf-8") as f:
    sites = json.load(f)

for site in sites:
    module = site["script"]  # era "module"
    print(f"Generating feed for: {module}")
    subprocess.run(["python", "generate_rss.py", module])
