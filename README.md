# Store Hours Pipeline 🏪

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?style=flat&logo=apacheairflow&logoColor=white)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?style=flat&logo=elasticsearch&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=flat&logo=openstreetmap&logoColor=white)

**End-to-End Data Engineering Pipeline für Öffnungszeiten von Geschäften.**

Automatisierte ETL-Pipeline, die Öffnungszeiten-Daten aus OpenStreetMap (Overpass API) extrahiert, verarbeitet und in Elasticsearch indexiert — vollständig orchestriert mit Apache Airflow und containerisiert mit Docker.

Entstanden als vollständiges Data-Engineering-Projekt im Studium (Wirtschaftsinformatik, Hochschule Worms).

---

## Architektur

```
OpenStreetMap (Overpass API)
         │
         ▼ scrape_overpass.js
    Rohdaten (JSON)
         │
         ▼ process_overpass.js
  Normalisierte Daten
  (Öffnungszeiten geparst,
   Koordinaten bereinigt)
         │
         ▼ index_elastic.js
    Elasticsearch Index
         │
         ▼
   Suchbare API für
   Öffnungszeiten-Abfragen

  Orchestrierung: Apache Airflow (Docker)
  Setup:          setup.sh (vollautomatisch)
```

---

## Funktionen

- **Automatisierte Datenerfassung** via Overpass API (OpenStreetMap) — kein manuelles Scraping
- **Öffnungszeiten-Parsing** — strukturierte Verarbeitung des OSM-Formats `Mo-Fr 09:00-18:00`
- **Elasticsearch-Indexierung** — volltext- und geo-suchbar
- **Airflow-Orchestrierung** — DAGs für Scheduling, Retry-Logik und Monitoring
- **Docker-Setup** — ein Befehl, alles läuft (`./setup.sh`)

---

## Projektstruktur

```
store-hours-pipeline/
├── airflow-docker/          # Docker Compose + Airflow DAGs
│   └── dags/                # Pipeline-Definitionen
├── data/                    # Rohdaten & verarbeitete Ausgabe
├── setup/                   # Konfigurationsdateien
├── scrape_overpass.js       # Schritt 1: Daten aus OpenStreetMap holen
├── process_overpass.js      # Schritt 2: Transformieren & normalisieren
├── index_elastic.js         # Schritt 3: In Elasticsearch indexieren
├── setup.sh                 # Vollautomatisches Setup
└── package.json
```

---

## Quick Start

### Voraussetzungen

- Docker & Docker Compose
- Node.js 18+
- Elasticsearch (lokal oder Cloud)

### Setup (vollautomatisch)

```bash
git clone https://github.com/guilloulearnlife/store-hours-pipeline.git
cd store-hours-pipeline
chmod +x setup.sh
./setup.sh
```

Das Skript richtet Elasticsearch, Airflow und alle Abhängigkeiten automatisch ein.

### Pipeline manuell ausführen

```bash
# Schritt 1 — Daten aus OpenStreetMap holen
node scrape_overpass.js

# Schritt 2 — Verarbeiten & normalisieren
node process_overpass.js

# Schritt 3 — In Elasticsearch indexieren
node index_elastic.js
```

### Airflow starten

```bash
cd airflow-docker
docker compose up -d
# Dashboard: http://localhost:8080
```

---

## Tech Stack

| Komponente | Technologie |
|---|---|
| Datenquelle | OpenStreetMap / Overpass API |
| Verarbeitung | Python, Node.js (JavaScript) |
| Orchestrierung | Apache Airflow |
| Suche & Indexierung | Elasticsearch |
| Containerisierung | Docker, Docker Compose |
| Setup-Automatisierung | Shell Script |

---

## Projektkontext

Entwickelt als eigenständiges Data-Engineering-Projekt zur Vertiefung von ETL-Pipelines, Workflow-Orchestrierung und Suchanwendungen. Zeigt den vollständigen Datenpfad von der öffentlichen API bis zur durchsuchbaren Datenbank.

---

## Lizenz

MIT — freie Verwendung mit Quellenangabe.
