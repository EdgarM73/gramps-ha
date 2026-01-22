# HACS Default Repository Einreichung

Anleitung zur Einreichung von Gramps HA in die offiziellen HACS-Repositories.

## Voraussetzungen (bereits erfüllt ✅)

- ✅ GitHub Repository: https://github.com/EdgarM73/gramps-ha
- ✅ `hacs.json` vorhanden und korrekt
- ✅ `manifest.json` mit korrekter Struktur
- ✅ Release v1.0.0 Tag erstellt
- ✅ README.md mit Installationsanleitung
- ✅ Icon/Logo (icon.png)
- ✅ Übersetzungen in mehreren Sprachen

## Schritt 1: GitHub Release erstellen

⚠️ **Wichtig:** HACS benötigt einen offiziellen GitHub Release (nicht nur ein Tag)!

1. Gehe zu: https://github.com/EdgarM73/gramps-ha/releases/new

2. **Einstellungen:**
   - **Choose a tag:** v1.0.0 (aus Dropdown wählen)
   - **Release title:** `v1.0.0 - Gramps HA Integration`
   - **Description:** (siehe unten)

3. **Release-Beschreibung:**

```markdown
# Gramps HA Integration v1.0.0

Erste offizielle Version der Gramps Web Integration für Home Assistant.

## Features

- 🎂 **6 Geburtstags-Sensoren** - Jeweils aufgeteilt in Name, Alter und Datum
- 📅 **Automatische Berechnung** - Tage bis zum nächsten Geburtstag
- 🎉 **Altersanzeige** - Zeigt das kommende Alter der Person
- 🔄 **Auto-Update** - Aktualisierung alle 6 Stunden
- 🔐 **Authentifizierung** - Unterstützung für geschützte Gramps Web Instanzen
- 🌍 **5 Sprachen** - Deutsch, Englisch, Französisch, Italienisch, Bosnisch
- 🧩 **Nachname-Filter** - Gezielte Anzeige nach Familiennamen
- 👤 **Nur Lebende** - Automatischer Filter für verstorbene Personen

## Sensoren

Die Integration erstellt für jeden der nächsten 6 Geburtstage drei separate Sensoren:
- **Name** - Person mit dem nächsten Geburtstag
- **Alter** - Wie alt die Person wird
- **Datum** - Wann der Geburtstag stattfindet

Zusätzlich ein Aggregat-Sensor mit allen anstehenden Geburtstagen.

## Installation

### Via HACS (empfohlen)

1. HACS öffnen → Integrationen
2. ⋮ (Menü) → Custom repositories
3. Repository-URL: `https://github.com/EdgarM73/gramps-ha`
4. Kategorie: **Integration**
5. Nach "Gramps HA" suchen und installieren
6. Home Assistant neu starten

### Manuelle Installation

Siehe [README.md](https://github.com/EdgarM73/gramps-ha#installation)

## Konfiguration

1. Einstellungen → Geräte & Dienste → Integration hinzufügen
2. "Gramps HA" suchen
3. Gramps Web URL eingeben (z.B. `http://localhost:5000`)
4. Optional: Benutzername, Passwort, Nachname-Filter

## Dashboard-Vorlagen

Vollständige Lovelace-Beispiele (Grid, Markdown, Entities) in [EXAMPLES.md](https://github.com/EdgarM73/gramps-ha/blob/main/EXAMPLES.md)

## Changelog

### v1.0.0 (2026-01-22)
- Initial Release
- 6 Geburtstags-Sensoren (Name/Alter/Datum)
- Gramps Web API Integration
- 5 Sprach-Übersetzungen
- Nachname-Filter
- Automatische Aktualisierung
- HACS-Unterstützung
```

4. **Set as the latest release** ✅ (ankreuzen)
5. **Publish release** klicken

## Schritt 2: HACS Default Repository Fork erstellen

1. Gehe zu: https://github.com/hacs/default

2. Klicke oben rechts auf **Fork**

3. Erstelle den Fork in deinem Account

## Schritt 3: Integration in HACS Default eintragen

1. In deinem Fork, öffne die Datei: **integration**

2. Füge deine Integration alphabetisch sortiert hinzu:

```json
{
  "name": "EdgarM73/gramps-ha",
  "description": "Gramps Web genealogy integration - displays upcoming birthdays from your family tree"
}
```

Die Datei ist eine JSON-Liste, also zwischen zwei anderen Einträgen einfügen:

```json
[
  ...
  {
    "name": "andersonshatch/midea-ac-py",
    "description": "Control Midea air conditioners via LAN"
  },
  {
    "name": "EdgarM73/gramps-ha",
    "description": "Gramps Web genealogy integration - displays upcoming birthdays from your family tree"
  },
  {
    "name": "elad-bar/ha-edgeos",
    "description": "Ubiquiti EdgeOS integration"
  },
  ...
]
```

## Schritt 4: Pull Request erstellen

1. Commit deine Änderungen in deinem Fork

2. Gehe zu: https://github.com/hacs/default/compare

3. Klicke **compare across forks**

4. **Head repository:** Dein Fork (EdgarM73/default)
5. **Base repository:** hacs/default

6. Erstelle Pull Request mit:
   - **Title:** `Add EdgarM73/gramps-ha`
   - **Description:**

```markdown
## Description
Add Gramps HA - A Home Assistant integration for Gramps Web genealogy software.

## Repository
https://github.com/EdgarM73/gramps-ha

## Features
- Displays next 6 birthdays from Gramps Web genealogy database
- Separate sensors for name, age, and date
- Surname filter support
- Auto-update every 6 hours
- Translations: DE, EN, FR, IT, BS
- HACS-ready with proper structure

## Checklist
- [x] Repository is public
- [x] Valid `hacs.json` present
- [x] Valid `manifest.json` present
- [x] Release v1.0.0 created
- [x] README.md with installation instructions
- [x] Icon included
- [x] Integration follows Home Assistant guidelines
- [x] No breaking changes expected
```

## Schritt 5: Nach PR-Einreichung

1. **Warte auf Review** - HACS-Team prüft deinen PR (kann 1-7 Tage dauern)

2. **Automatische Checks** - GitHub Actions prüfen:
   - JSON-Syntax korrekt
   - Repository existiert
   - Release vorhanden
   - `hacs.json` valide

3. **Feedback umsetzen** - Falls Änderungen nötig sind

4. **Merge** - Nach Genehmigung wird dein PR gemerged

5. **Verfügbarkeit** - Innerhalb von 24h in HACS sichtbar

## Alternative: Vorerst als Custom Repository

**Sofort nutzbar ohne Warten auf HACS-Approval:**

Benutzer können dein Repository direkt hinzufügen:

1. HACS öffnen → Integrationen
2. ⋮ → Custom repositories
3. `https://github.com/EdgarM73/gramps-ha`
4. Kategorie: Integration

## Wichtige Links

- **Dein Repository:** https://github.com/EdgarM73/gramps-ha
- **HACS Default Repo:** https://github.com/hacs/default
- **HACS Dokumentation:** https://hacs.xyz/docs/publish/start
- **Integration Requirements:** https://hacs.xyz/docs/publish/integration

## Troubleshooting

### "Release not found"
- Stelle sicher, dass v1.0.0 als GitHub Release (nicht nur Tag) existiert
- Check: https://github.com/EdgarM73/gramps-ha/releases

### "Invalid hacs.json"
```bash
# Validieren:
cd "c:\Users\fake\OneDrive\Dokumente\dev\birthday"
cat hacs.json
```

### "Manifest validation failed"
```bash
# Validieren:
cat custom_components/gramps_ha/manifest.json
```

## Nach erfolgreicher Aufnahme

Benutzer können die Integration direkt in HACS suchen:
1. HACS → Integrationen
2. Suche: "Gramps HA" oder "birthday" oder "genealogy"
3. Installieren

---

**Status:** ⏳ Vorbereitet, bereit für Einreichung
**Nächster Schritt:** GitHub Release erstellen (siehe Schritt 1)
