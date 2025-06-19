name: Genera e aggiorna feed RSS

on:
  schedule:
    - cron: '0 6 * * *'  # Ogni giorno alle 6 del mattino UTC (8:00 italiane)
    - cron: '0 11 * * *' # Ogni giorno alle 11:00 UTC (13:00 italiane)
  workflow_dispatch:  # Permette avvio manuale

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Configura Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Installa dipendenze
        run: pip install -r requirements.txt

      - name: Lista file repository
        run: ls -la

      - name: Esegui generazione feed (Altissimo)
        run: python Altissimo.py || echo "⚠️ Errore durante generazione Altissimo, proseguo"

      - name: Esegui generazione feed (Malo)
        run: python Malo.py || echo "⚠️ Errore durante generazione Malo, proseguo"

      - name: Esegui generazione feed (Arzignano)
        run: python Arzignano.py || echo "⚠️ Errore durante generazione Arzignano, proseguo"

      - name: Commit e push aggiornamenti
        run: |
          git config --global user.name "github-actions"
          git config --global user.email "github-actions@github.com"
          git add *.xml
          git commit -m "Aggiornamento automatico feed RSS" || echo "Nessuna modifica"
          git push
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
