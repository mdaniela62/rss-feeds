import importlib
import sys

def generate_feed(module_name):
    try:
        # Importa dinamicamente lo script del comune
        module = importlib.import_module(f"comuni.{module_name}")
    except ModuleNotFoundError:
        print(f"[KO] Errore: il modulo comuni/{module_name}.py non esiste.")
        return

    # Se il modulo ha la funzione generate_feed, la esegue
    if hasattr(module, "generate_feed"):
        module.generate_feed()
        print(f"[OK] Feed generato con successo per: {module_name}")
    else:
        print(f"[KO] Errore: il modulo '{module_name}' non ha la funzione generate_feed().")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python generate_rss.py <nome_modulo>")
    else:
        generate_feed(sys.argv[1])
