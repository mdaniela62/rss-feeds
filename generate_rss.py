import importlib
import sys
import os
from jinja2 import Template
from datetime import datetime

def load_template():
    with open("template.xml", "r", encoding="utf-8") as f:
        return Template(f.read())

def generate_feed(module_name):
    module = importlib.import_module(f"comuni.{module_name}")
# Esegui la funzione generate_feed() o main() se esistono
if hasattr(module, "generate_feed"):
    module.generate_feed()
elif hasattr(module, "main"):
    module.main()
else:
    print(f"⚠️  Nessuna funzione trovata in {module_name}")

    items = module.get_items()
    info = module.SITE_INFO

    template = load_template()
    output = template.render(
        title=info["name"],
        link=info["url"],
        description=f"Ultime notizie da {info['name']}",
        lastBuildDate=datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z"),
        items=items
    )

    os.makedirs(os.path.dirname(info["output"]), exist_ok=True)
    with open(info["output"], "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_rss.py <nome_script>")
    else:
        generate_feed(sys.argv[1])
