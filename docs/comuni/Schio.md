# Comune di Schio

- **URL ufficiale notizie:** [https://www.comune.schio.vi.it/Novita](https://www.comune.schio.vi.it/Novita)
- **Script associato:** `schio_playwright.py`
- **Output feed RSS:** `feeds/feed_schio.xml`

---

## Struttura HTML osservata
- Contenitore articolo: `<div class="card card-teaser">`
- Titolo: `h3.card-title`
- Link: `a.read-more`
- Data: `div.mt-1 strong:contains("Data di pubblicazione")`

---

## Note tecniche
- Usa **Playwright** (necessario per caricare correttamente la pagina)  
- Gestione cookies: ✅ Sì (accettazione banner)  
- Altre osservazioni: serve attendere caricamento JS

---

## Stato attuale
- ✅ Funzionante  
- Ultima verifica: 16/08/2025
