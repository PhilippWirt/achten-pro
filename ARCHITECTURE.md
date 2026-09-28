# achten.pro / Playfight – Seitenarchitektur

## Verbindliche Quelle

Die vier Angebotsseiten und zwei Datenschutzseiten werden nicht unabhängig bearbeitet. Verbindlich sind:

```text
source/
├── templates/
│   ├── achten-pro.html
│   └── playfight.html
├── locales/
│   ├── achten-pro.de.json
│   ├── achten-pro.en.json
│   ├── playfight.de.json
│   └── playfight.en.json
├── legal/
│   ├── datenschutz.html
│   └── privacy.html
└── shared/
    ├── language-switch.html
    ├── language-switch.js
    ├── navigation.json
    └── styles.css
```

`build.py` erzeugt daraus:

```text
/index.html                 Deutsch, achten.pro-Standard
/en/index.html              Englisch
/playfight/index.html       Englisch, Playfight-Standard
/playfight/de/index.html    Deutsch
/datenschutz.html           Deutsche Datenschutzerklärung
/en/privacy.html            Englische Datenschutzerklärung
```

Die erzeugten HTML-Dateien sind Ausgaben, keine eigenständigen redaktionellen Quellen.

## Arbeitsfluss

```text
Templates + Locale-Daten + gemeinsame Bausteine
                        ↓
                 python3 build.py
                        ↓
               sechs statische Seiten
                        ↓
        python3 tests/verify_build.py
```

Der Test führt den Build zweimal aus und prüft:

- identische Hashes bei beiden Durchläufen,
- Struktur- und ID-Parität je Sprachpaar,
- interne Links und Bildpfade,
- `lang`, Canonical und `hreflang`,
- JavaScript-Syntax,
- fehlende oder doppelte Elemente,
- Position von Personal Training unter Experience,
- Entfernung der alten Route `playfight/en`.

## Sprachlogik

- Keine automatische Sprachweiterleitung.
- DE/EN sind normale Links und funktionieren ohne JavaScript.
- Eine Auswahl wird nur optional im Browser gespeichert.
- Getrennte Schlüssel: `lang_ap` und `lang_pf`.
- achten.pro verweist sprachgleich auf Playfight.
- Playfight verweist sprachgleich zurück zum Personal Training.

## Gestaltung

- Überschriften: `Newsreader`
- Fließtext und Navigation: `IBM Plex Sans`
- Personal Training ist in der Playfight-Navigation und im Inhalt dem Bereich Experience/Erfahrung untergeordnet.

## Prüfung und Rückfall

- Lokale Phase-3-Belege: `/home/philipp/worktrees/achten-pro-phase0-audit-20260819_2215/`
- Phase-3-Branch: `phase3-language-build`
- Baseline vor den lokalen Reparaturen: `3e68e7d0efcae8c6aee539e1177b37543e98eadc`
- Externe Sicherungskopien liegen im Audit-Verzeichnis unter `backups/`.
- Vor Veröffentlichung erneut Gesamt-QA und Git-Diff prüfen.
- Kein Push oder Deployment ohne ausdrückliche Freigabe.
