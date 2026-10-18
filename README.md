# Homepage Tischtennis TSV Dettingen/Erms

Die Seite zeigt Spielplan, Ergebnisse und Tabellen aller Mannschaften. Die Daten kommen aus **click-TT des TTBW** – genau die Daten, die auch mytischtennis.de anzeigt. Ein Abruf-Job holt sie **alle 2 Stunden** automatisch und veröffentlicht die Seite neu. Niemand muss etwas von Hand eintragen.

```
src/page.html              Quelltext der Homepage (hier Design und Texte ändern)
build.py                   baut daraus site/index.html: python build.py
site/index.html            die fertige Homepage
site/assets/               Logo und Schrift (Archivo, SIL Open Font License)
site/data.json             die aktuellen Daten (wird automatisch überschrieben)
scraper/fetch_clicktt.py   holt die Daten aus click-TT
scraper/config.json        Mannschaften, Ligen, Halle, Trainingszeiten, Kontakt
scraper/test_parser.py     Test des Abrufs
.github/workflows/update.yml   Zeitplan (alle 2 Std.) + Veröffentlichung
```

## Einrichtung (einmalig, ca. 15 Minuten, kostenlos)

1. Auf github.com ein Konto anlegen (z. B. für die Abteilung) und ein **neues öffentliches Repository** erstellen, z. B. `tt-dettingen`.
2. Den Inhalt dieses Ordners hochladen (Website: „Add file“ → „Upload files“, den Ordner `.github` mit hochladen).
3. Im Repository: **Settings → Pages → Source: „GitHub Actions“** auswählen.
4. **Actions → „Ergebnisse aktualisieren & Seite veröffentlichen“ → „Run workflow“** einmal von Hand starten.
5. Nach ca. 1 Minute ist die Seite online unter `https://<konto>.github.io/tt-dettingen/`.

Ab dann läuft alles allein. Sofort aktualisieren: Schritt 4 wiederholen.

### Eigene Adresse (optional)
Unter Settings → Pages → „Custom domain“ z. B. `tischtennis.tsvdettingen-erms.de` eintragen und beim Webhoster des Hauptvereins einen CNAME-Eintrag auf `<konto>.github.io` setzen lassen. Alternativ auf der bestehenden TSV-Seite unter „Abteilungen → Tischtennis“ einfach auf die neue Adresse verlinken.

## Inhalte anpassen – `scraper/config.json`

- **Trainingszeiten** (aktuell leer, dann erscheint ein Hinweis auf die Abteilungsleitung):
  ```json
  "training": [
    { "day": "Dienstag", "time": "18:00–20:00 Uhr", "group": "Jugend" },
    { "day": "Freitag",  "time": "19:30–22:00 Uhr", "group": "Erwachsene" }
  ]
  ```
- **Kontakt**: `contact`, `email`, `instagram`.
- Nach einer Änderung startet die Seite automatisch neu (Push auf `main`).

## Neue Saison (einmal im Jahr, im Sommer)

In `config.json` ändern: `season`, `season_from`, `season_to`, `mytt_season` und für jede Mannschaft `championship`, `group`, `short`, `league`, `mytt`.
Die Werte stehen auf click-TT: Vereinsseite → „Mannschaften und Ligeneinteilung“ → Liga anklicken; in der Adresse stehen `championship=…` und `group=…`. Das Kürzel (`short`, z. B. `E BOL`) steht in der Spalte „Liga“ des Vereinsspielplans. Kommt eine Mannschaft dazu (z. B. Jugend), einfach einen weiteren Eintrag anlegen.

## Wenn etwas nicht stimmt

- Unter **Actions** sieht man jeden Lauf. Ein roter Lauf heißt: click-TT war nicht erreichbar oder hat den Seitenaufbau geändert. Die Seite zeigt dann die letzten Daten weiter an.
- Lokal testen: `pip install requests beautifulsoup4`, dann `python scraper/test_parser.py` und `python scraper/fetch_clicktt.py --dry-run`.
- GitHub pausiert Zeitpläne in Repositories ohne Aktivität nach 60 Tagen. Da der Job bei jedem neuen Ergebnis die Daten speichert, passiert das in der Saison nicht; nach der Sommerpause ggf. unter Actions wieder aktivieren.

## Design und Texte ändern

Texte und Design stehen in `src/page.html`. Nach einer Änderung `python build.py` ausführen und hochladen. Die Schrift wird mit der Seite ausgeliefert und nicht von Google geladen, das ist datenschutzrechtlich unkritisch.
