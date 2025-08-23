import os

def check_scripts():
    comuni_dir = "comuni"
    problems = []

    for filename in os.listdir(comuni_dir):
        if filename.endswith(".py"):
            path = os.path.join(comuni_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if "return feed.writeString(" not in content:
                problems.append(filename)

    if problems:
        print("⚠️ Script da aggiornare (non restituiscono la stringa XML):")
        for p in problems:
            print(" -", p)
    else:
        print("✅ Tutti gli script restituiscono correttamente la stringa XML")

if __name__ == "__main__":
    check_scripts()
