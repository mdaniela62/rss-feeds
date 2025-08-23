import json
import subprocess
import os

def test_all():
    with open("sites_list.json", "r", encoding="utf-8") as f:
        sites = json.load(f)

    ok = []
    errors = []

    for site in sites:
        script_name = site.get("script")
        if not script_name:
            continue

        print(f"🚀 Test feed: {script_name}")
        result = subprocess.run(
            ["python", "generate_rss.py", script_name],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # verifica che il file xml esista e non sia vuoto
            xml_path = os.path.join("feeds", f"{script_name}.xml")
            if os.path.exists(xml_path) and os.path.getsize(xml_path) > 0:
                print(f"✅ OK: {xml_path}")
                ok.append(script_name)
            else:
                print(f"⚠️ Nessun file XML creato per {script_name}")
                errors.append(script_name)
        else:
            print(f"❌ Errore nello script {script_name}")
            print("   STDERR:", result.stderr.strip())
            errors.append(script_name)

    print("\n--- RISULTATO ---")
    print("✅ OK:", ok)
    print("❌ Errori:", errors)

if __name__ == "__main__":
    test_all()
