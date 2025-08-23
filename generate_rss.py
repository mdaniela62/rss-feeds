import json
import sys
import os
import importlib
import traceback
import inspect
import asyncio

SITES_LIST = "sites_list.json"

def load_site(script_name: str):
    script_name = script_name.strip().removesuffix(".py")
    with open(SITES_LIST, "r", encoding="utf-8") as f:
        sites = json.load(f)
    if isinstance(sites, dict) and "sites" in sites:
        sites = sites["sites"]
    for site in sites:
        if isinstance(site, str):
            if site.strip().lower() == script_name.lower():
                return {"name": site, "script": script_name, "output": f"feeds/{script_name}.xml"}
        elif isinstance(site, dict):
            if site.get("script", "").strip().lower() == script_name.lower():
                site["output"] = site.get("output") or f"feeds/{script_name}.xml"
                return site
    return None

def pick_func(module, script_name: str):
    # ordine di preferenza
    candidates = [
        "generate_feed",
        f"scrape_{script_name}",
        "generate",
        "build_feed",
        "make_feed",
        "run",
        "main",
        # async variants
        "generate_feed_async",
        "generate_async",
    ]
    for name in candidates:
        fn = getattr(module, name, None)
        if callable(fn):
            return fn, name
    return None, None

def result_to_xml(res):
    # accetta str, bytes, o oggetti feedgenerator con writeString
    if isinstance(res, str):
        return res
    if isinstance(res, (bytes, bytearray)):
        try:
            return res.decode("utf-8")
        except Exception:
            return res.decode(errors="replace")
    if hasattr(res, "writeString") and callable(getattr(res, "writeString")):
        try:
            return res.writeString("utf-8")
        except Exception:
            return None
    return None

def call_func(func, site):
    # Prova firma (site), poi senza argomenti
    if inspect.iscoroutinefunction(func):
        try:
            return asyncio.run(func(site))
        except TypeError:
            return asyncio.run(func())
    else:
        try:
            return func(site)
        except TypeError:
            return func()

def main():
    if len(sys.argv) < 2:
        print("[KO] Errore: manca l'argomento <script>")
        sys.exit(1)

    script_name = sys.argv[1].strip().removesuffix(".py")
    site = load_site(script_name)
    if not site:
        print(f"[KO] Errore: '{script_name}' non trovato in {SITES_LIST}")
        sys.exit(1)

    try:
        module = importlib.import_module(f"comuni.{script_name}")
    except ModuleNotFoundError as e:
        if e.name in (f"comuni.{script_name}", "comuni"):
            print(f"[KO] Errore: il modulo comuni/{script_name}.py non esiste.")
        else:
            print(f"[KO] Errore: manca un modulo richiesto da comuni/{script_name}.py -- {e.name}")
        sys.exit(1)
    except Exception:
        print("[KO] Errore durante l'import del modulo:")
        traceback.print_exc()
        sys.exit(1)

    func, fname = pick_func(module, script_name)
    if func is None:
        print(f"[KO] Errore: in comuni/{script_name}.py non c'è una funzione compatibile "
              f"(attese: generate_feed, scrape_{script_name}, generate, build_feed, make_feed, run, main, "
              f"o varianti async).")
        sys.exit(1)

    # Chiama la funzione del comune
    try:
        res = call_func(func, site)
    except Exception:
        print("[KO] Errore durante l'esecuzione della funzione "
              f"'{fname}' in comuni/{script_name}.py:")
        traceback.print_exc()
        sys.exit(1)

    xml = result_to_xml(res)
    output_path = site.get("output") or f"feeds/{script_name}.xml"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if xml is None:
        # compatibilità col vecchio pattern: se il modulo ha scritto da solo il file, consideriamo OK
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"[INFO]  Nota: la funzione '{fname}' non ha restituito la stringa XML, "
                  f"ma il file sembra già generato da comuni/{script_name}.py -- {output_path}")
            print(f"[OK] Feed generato: {output_path}")
            sys.exit(0)
        else:
            print(f"[KO] La funzione '{fname}' in comuni/{script_name}.py non ha restituito la stringa XML "
                  f"e non è stato trovato alcun file generato in '{output_path}'. "
                  f"Aggiorna lo script per fare `return feed.writeString(\"utf-8\")`.")
            sys.exit(1)

    # scriviamo noi l'XML
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"[OK] Feed generato: {output_path}")

if __name__ == "__main__":
    main()
