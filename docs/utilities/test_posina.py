from comuni import posina

items = posina.get_items()
print(f"🔍 Trovati {len(items)} articoli")
for item in items:
    print("-", item["title"], "->", item["link"], "|", item["date"])
    print("  Desc:", item["desc"][:80], "..." if item["desc"] else "")
