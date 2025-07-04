# DND Companion API

Eine REST-API zur Verwaltung von Dungeons & Dragons Charakteren, sowie deren Zaubern und Items. Dieses Projekt wurde als Portfolio-Stück im Rahmen einer Weiterbildung entwickelt und auf einem eigenen Server produktiv deployed.

**Live API-Dokumentation (Swagger UI):** [https://api.luns.dev/docs](https://api.luns.dev/docs)

## Projektbeschreibung
Ziel ist es, Spieler*innen eine einfache Möglichkeit zu geben, Informationen zu Zaubern und Items ihrer Charakteren auf **Deutsch** abzurufen, zu speichern und zu verwalten. Items und Zauber werden beim ersten Hinzufügen zu einem Charakter automatisch aus der externen D&D 5e API übernommen, via DeepL ins Deutsche übersetzt und anschließend lokal in der PostgreSQL-Datenbank gespeichert.

## Features

-   **Benutzerverwaltung:** Sichere Registrierung und Login über JWT-Authentifizierung.
-   **Charakterverwaltung:** Vollständige CRUD-Operationen für Charaktere.
-   **Dynamische Datenanreicherung:**
    -   Automatisches Laden von Zauber- und Item-Daten aus der externen `dnd5eapi.co`.
    -   Automatische Übersetzung der Daten ins Deutsche via DeepL API.
    -   Lokales Caching der angereicherten Daten zur Performance-Steigerung und Reduzierung von API-Anfragen.
-   **Rechteverwaltung:** Jeder Benutzer kann nur seine eigenen Charaktere und deren Verknüpfungen einsehen und bearbeiten.

## Architektur & Deployment

Die Anwendung ist auf einem eigenen **Ubuntu-Server** gehostet und folgt modernen DevOps-Praktiken.

-   **Webserver:** **Nginx** dient als Reverse Proxy, der Anfragen entgegennimmt und für SSL-Terminierung (HTTPS) zuständig ist.
-   **Anwendungsserver:** **Uvicorn** führt die FastAPI-Anwendung aus.
-   **Prozess-Management:** Ein **Systemd-Service** stellt sicher, dass die Anwendung im Hintergrund stabil läuft und bei einem Neustart des Servers automatisch wieder gestartet wird.
-   **CI/CD:** Eine **GitHub Actions Pipeline** sorgt für automatisches Deployment. Jeder Push auf den `main`-Branch löst einen Workflow aus, der den neuesten Code auf dem Server via SSH abruft (`git pull`) und den Service neu startet.

## Tech Stack

-   **Backend:** Python, FastAPI, Pydantic
-   **Datenbank:** PostgreSQL mit SQLAlchemy als ORM
-   **Authentifizierung:** Passlib, bcrypt, python-jose für JWT
-   **Externe APIs:** dnd5eapi.co, DeepL API

## API-Dokumentation

Die vollständige und interaktive API-Dokumentation wird automatisch von FastAPI generiert und ist unter folgendem Link erreichbar. Dort können alle Endpunkte direkt im Browser getestet werden:

https://api.luns.dev/docs

## Datenmodell

Das Datenbankschema wurde mit `dbdiagram.io` visualisiert und zeigt die Beziehungen zwischen Benutzern, Charakteren, Items und Zaubern.

https://dbdiagram.io/d/6849a0a7a463a450da194ef0

## Projektstatus

Dieses Repository dient als Portfolio-Projekt. Es ist öffentlich, um die Implementierung, die Code-Struktur und die Deployment-Architektur zu demonstrieren. Ein lokales Setup oder eine aktive Weiterentwicklung durch Dritte ist daher nicht vorgesehen oder supportet.