# DND Companion 

## Projektbeschreibung
DND Companion ist für die Verwaltung von Dungeons & Dragons Charakteren, sowie deren Zaubern und Items.  
Ziel ist es, Spieler*innen eine einfache Möglichkeit zu geben, Informationen zu Zaubern und Items ihrer Charakteren auf **Deutsch** abzurufen, zu speichern und zu verwalten.  
Items und Zauber werden beim ersten Hinzufügen zu einem Charakter automatisch aus der externen D&D 5e API übernommen, ins Deutsch übersetzt und anschließend lokal gespeichert.

## Features

- **Benutzerverwaltung** Registrierung, Login
- **Charakterverwaltung:** Anlegen, Anzeigen, Bearbeiten, Löschen von Charakteren
- **Zauber:** Anlegen, Anzeigen, Zuordnen/Entfernen von Zaubern zu/von Charakteren (inkl. Integration externer D&D 5e API)
- **Items:** Anlegen, Anzeigen, Zuordnen/Entfernen von Items zu/von Charakteren (inkl. Integration externer D&D 5e API)
- **Rechteverwaltung:** Jeder Benutzer sieht und bearbeitet nur seine eigenen Charaktere/Items/Spells

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [dnd5eapi.co](https://www.dnd5eapi.co/) als externe Quelle für D&D-Daten
- [DeepL API](https://developers.deepl.com/docs) für Übersetzung von D&D-Daten

## Datenmodell

*ER Bild folgt*

**Wichtige Tabellen:**

- **users**: Benutzerverwaltung
- **characters**: D&D-Charaktere, gehören zu einem Benutzer
- **items**: D&D-Items (allgemeine Datenbank)
- **spells**: D&D-Zauber (allgemeine Datenbank)
- **character_items**: Zuordnungstabelle Charakter ↔ Item 
- **character_spells**: Zuordnungstabelle Charakter ↔ Spell
