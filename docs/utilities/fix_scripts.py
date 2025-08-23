import os
import re

def fix_scripts():
    comuni_dir = "comuni"
    fixed = []

    for filename in os.listdir(comuni_dir):
        if filename.endswith(".py"):
            path = os.path.join(comuni_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # controlla se manca il return corretto
            if "return feed.writeString(" not in content:
                # controlla che nello script ci sia un feed RSS
                if "Rss201rev2Feed(" in content and "def generate_feed(" in content:
                    # cerchiamo la chiusura della funzione generate_feed
                    match = re.search(r"(def generate_feed\(.*\):)", content)
                    if match:
                        # aggiungiamo il return in fondo al file (rientrato di 4 spazi)
                        new_content = content.rstrip() + "\n\n    return feed.writeString(\"utf-8\")\n"

                        with open(path, "w", encoding="utf-8") as f:
                            f.write(new_content)

                        fixed.append(filename)

    if fixed:
        print("✅ Aggiunto return mancante nei seguenti script:")
        for f in fixed:
            print(" -", f)
    else:
        print("👌 Tutti gli script erano già corretti")

if __name__ == "__main__":
    fix_scripts()
