import subprocess

comuni = [
    "altissimo",
    "arzignano",
    "barbaranomossano",
    "breganze",
    "cartigliano",
    "castelgomberto",
    "gambellara",
    "malo",
    "monteviale",
    "posina",
    "schiavon",
    "schio",
    "tezze",
    "torrebelvicino",
    "velodastico",
    "vallidelpasubio"
]

for comune in comuni:
    print(f"\n🚀 Generating feed for: Comune di {comune.capitalize()}")
    try:
        subprocess.run(["python", f"comuni/{comune}.py"], check=True)
        print("[OK] Done")
    except subprocess.CalledProcessError as e:
        print(f"[KO] Errore durante l'esecuzione di comuni/{comune}.py: {e}")
