"""
generate_rss.py
Funziona in doppia modalità:
- main() -> genera tutti i feed leggendo sites_list.json
- main(site_or_script) -> genera solo il singolo sito indicato. `site_or_script`
  può essere il dict preso da sites_list.json oppure la stringa path dello script.
"""

import importlib.util
import json
import os
import sys
import traceback

SITES_FILE = "sites_list.json"

def load_sites():
    with open(SITES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def find_site_by_script(script_path):
    """Cerca la voce sites_list.json corrispondente al path dello script. 
    Se non la trova, ritorna un dict minimo."""
    sites = load_sites()
    for s in sites:
        if s.get("script") == script_path:
            return s
    # fallback minimale
    return {"script": script_path, "name": os.path.splitext(os.path.basename(script_path))[0]}

def load_module(path):
    """Import dinamico sicuro del file path; crea un module name unico basato sull'hash del path."""
    abs_path = os.path.abspath(path)
    module_name = f"module_{abs(hash(abs_path))}"
    spec = importlib.util.spec_from_file_location(module_name, abs_path)
    mod = importlib.util.module_from_spec(spec)
    # assicuriamoci di non lasciare una vecchia entry con lo stesso nome
    sys.modules.pop(module_name, None)
    spec.loader.exec_module(mod)
    return mod

def call_func(func, site=None):
    """Chiama func con site se lo supporta, altrimenti senza argomenti."""
    try:
        return func(site)
    except TypeError:
        return func()

def process_site(site):
    """Esegue il singolo sito (site è un dict che contiene almeno 'script')."""
    script_path = site.get("script")
    site_name = site.get("name", script_path)

    # 🔧 correzione: se lo script è solo un nome corto, aggiungi cartella ed estensione
    if script_path and not os.path.sep in script_path and not script_path.endswith(".py"):
        script_path = os.path.join("comuni", script_path + ".py")

   # print(f"\n🚀 Generating feed for: {site_name}")

    if not script_path or not os.path.exists(script_path):
        print(f"[KO] Script non trovato: {script_path}")
        return

    try:
        mod = load_module(script_path)
        if hasattr(mod, "generate_feed"):
            call_func(mod.generate_feed, site)
            print(f"[OK] Feed generato per {site_name}")
        else:
            print(f"[KO] Nessuna funzione generate_feed in {script_path}")
    except Exception:
        print(f"[KO] Errore durante l'esecuzione di {script_path}:\n")
        traceback.print_exc()

def main(site_or_script=None):
    """
    Se site_or_script è None -> processa tutti i siti in sites_list.json.
    Se è un dict -> processa quel dict.
    Se è una stringa -> cerca la corrispondenza in sites_list.json (o fallback) e la processa.
    """
    if site_or_script:
        # caso: passo direttamente il dict
        if isinstance(site_or_script, dict):
            process_site(site_or_script)
            return
        # caso: passo lo script path come stringa
        process_site(find_site_by_script(site_or_script))
        return

    # modalità 'tutto'
    sites = load_sites()
    for s in sites:
        process_site(s)

if __name__ == "__main__":
    main()
