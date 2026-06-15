# ☕ FutureKawa — Suivi des stocks & conditions de stockage du café vert

Solution applicative **multi-pays** de suivi des lots de café vert et de **surveillance IoT** (température / humidité) des entrepôts, avec consolidation centrale au siège.

> MSPR TPRE814 — *Conception d'une solution applicative en adéquation avec l'environnement technique étudié* (RNCP 35584, Bloc 4).

---

## Sommaire

- [Présentation](#présentation)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Structure du dépôt](#structure-du-dépôt)
- [Prérequis](#prérequis)
- [Démarrage rapide](#démarrage-rapide)
- [Accès aux services](#accès-aux-services)
- [Configuration](#configuration)
- [Principaux endpoints API](#principaux-endpoints-api)
- [Tests](#tests)
- [État d'avancement & limitations connues](#état-davancement--limitations-connues)
- [Documentation associée](#documentation-associée)

---

## Présentation

FutureKawa est une entreprise de caféiculture présente au **Brésil, en Équateur et en Colombie**. La solution permet de :

- **centraliser le suivi des stocks** par pays et par entrepôt ;
- **garantir la traçabilité** des lots depuis leur entrée en stockage (logique **FIFO**) ;
- **surveiller automatiquement** les conditions de conservation via des capteurs IoT (MQTT) ;
- **détecter et signaler** les situations à risque (dérive de conditions, lot > 365 jours) par **email** ;
- préparer une **phase 2** d'automatisation des entrepôts (chauffage / humidification / aération).

L'architecture est **distribuée** : chaque pays dispose d'un backend local conteneurisé (base SQL + broker MQTT + API REST) ; le **siège** dispose d'un backend central qui interroge les pays et alimente le **frontend web**.

### Conditions idéales par pays

| Pays | Température idéale | Humidité idéale | Tolérance |
|------|:-----------------:|:---------------:|:---------:|
| 🇧🇷 Brésil   | 29 °C | 55 % | ± 3 °C / ± 2 % |
| 🇪🇨 Équateur | 31 °C | 60 % | ± 3 °C / ± 2 % |
| 🇨🇴 Colombie | 26 °C | 80 % | ± 3 °C / ± 2 % |

---

## Architecture

```mermaid
flowchart LR
    subgraph IoT["🌡️ Module IoT (entrepôt)"]
        ESP["ESP32 + DHT22<br/>(MicroPython / Wokwi)"]
    end

    subgraph Pays["🇧🇷 Backend pays — Brésil"]
        MQTT["Broker MQTT<br/>Mosquitto :1883"]
        API1["API REST pays<br/>FastAPI :8000"]
        DB[("PostgreSQL<br/>:5432")]
        API1 --- DB
    end

    subgraph Siege["🏢 Siège"]
        API2["API centrale<br/>FastAPI :8001"]
        FRONT["Frontend Web<br/>React + Vite :8090"]
    end

    ESP -- "MQTT publish<br/>temp / humidité" --> MQTT
    MQTT -- "souscription" --> API1
    API2 -- "HTTP (consolidation)" --> API1
    FRONT -- "HTTP" --> API2
```

> Schéma détaillé, justification des choix et flux complets : voir **[DOSSIER_TECHNIQUE.docx](DOSSIER_TECHNIQUE.docx)** (§2).

---

## Stack technique

| Couche | Technologies |
|--------|--------------|
| **IoT** | ESP32, capteur DHT22, MicroPython, simulation Wokwi |
| **Messagerie** | MQTT (broker Eclipse **Mosquitto**) |
| **Backends** | **Python 3.11**, **FastAPI**, SQLAlchemy, Pydantic, httpx, paho-mqtt |
| **Base de données** | **PostgreSQL 15** |
| **Alerting** | Service email SMTP (mode démo console) + flux **Node-RED** |
| **Frontend** | **React 19**, **Vite 8**, React Router 7, Tailwind CSS, graphiques SVG natifs |
| **Conteneurisation** | **Docker** / **Docker Compose** |

---

## Structure du dépôt

```
.
├── backend-brazil/        # Backend pays « exemple » (Brésil)
│   ├── app/
│   │   ├── main.py        # Routes API REST (FastAPI)
│   │   ├── models.py      # Modèles SQLAlchemy (pays, entrepôt, lot, mesure, alerte)
│   │   ├── crud.py        # Accès données
│   │   ├── alerts.py      # Moteur d'alertes (conditions + âge des lots)
│   │   ├── email_service.py  # Envoi des emails d'alerte (démo console si SMTP absent)
│   │   ├── mqtt.py        # Souscripteur MQTT → persistance des mesures
│   │   ├── seed.py        # Jeu de données de démonstration (idempotent)
│   │   └── database.py    # Connexion PostgreSQL
│   ├── mqtt_simulator.py  # Simulateur de capteur IoT (publie sur MQTT)
│   └── Dockerfile
├── backend-central/       # Backend central « siège » (consolidation multi-pays)
│   └── app/
│       ├── main.py        # Routes de consolidation + proxy vers les pays
│       ├── country_client.py  # Client HTTP vers les backends pays
│       └── config.py      # Registre des pays connectés
├── frontend/              # Application web React/Vite (dashboard)
├── ESP32/                 # Firmware & schéma Wokwi du module IoT
├── main.py                # Code MicroPython embarqué (ESP32 + DHT22)
├── Node-Red flows/        # Flux Node-RED d'alerting email
├── mosquitto/             # Configuration du broker MQTT
├── db/                    # Schéma SQL de référence
├── docker-compose.yml     # Orchestration de l'ensemble
├── README.md              # Ce fichier
├── DOSSIER_TECHNIQUE.docx # Dossier technique (archi, IoT, plans de tests)
└── DOCUMENTATION_UTILISATEUR.docx  # Guide d'utilisation métier
```

---

## Prérequis

- **Docker** et **Docker Compose** (v2)
- **Node.js ≥ 18** et **npm** (pour le frontend en mode développement)
- **Python ≥ 3.11** (optionnel, pour lancer le simulateur IoT depuis l'hôte)

---

## Démarrage rapide

### 1. Lancer le stack backend + IoT (base, broker, API pays, API centrale)

```bash
docker compose up -d postgres mosquitto brazil-api central-api
```

> ⚠️ Le service `frontend` du `docker-compose.yml` n'est **pas encore conteneurisé** (Dockerfile à fournir — voir [limitations](#état-davancement--limitations-connues)). On lance donc le front en mode développement (étape 2).

Au démarrage, le backend Brésil crée les tables et insère automatiquement un **jeu de données de démonstration** (1 pays, 1 exploitation, 1 entrepôt, 5 lots, 3 mesures).

### 2. Lancer le frontend

```bash
cd frontend
npm install
npm run dev
```

Le dashboard est accessible sur **http://localhost:5173**.

### 3. (Optionnel) Simuler des relevés capteurs IoT

Dans un terminal séparé, publier des mesures sur le broker MQTT :

```bash
cd backend-brazil
pip install -r requirements.txt
python mqtt_simulator.py            # données normales
python mqtt_simulator.py --anomalies  # déclenche des alertes (valeurs hors seuil)
```

Le backend persiste les mesures reçues et **lève automatiquement les alertes** (et envoie les emails — affichés en console en mode démo).

### Tout arrêter

```bash
docker compose down          # arrête les conteneurs
docker compose down -v       # + supprime les données PostgreSQL
```

---

## Accès aux services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend (dev) | http://localhost:5173 | Dashboard web |
| API pays (Brésil) | http://localhost:8000 | API REST locale + docs Swagger sur `/docs` |
| API centrale (siège) | http://localhost:8001 | Consolidation multi-pays + `/docs` |
| PostgreSQL | `localhost:5432` | base `futurkawa_db` (`postgres` / `password`) |
| Mosquitto (MQTT) | `localhost:1883` | Broker MQTT |

> 💡 La documentation interactive **Swagger** est disponible sur `/docs` de chaque API (générée automatiquement par FastAPI).

---

## Configuration

Les paramètres se définissent via variables d'environnement (voir `docker-compose.yml`).

### Backend pays (`brazil-api`)

| Variable | Défaut | Rôle |
|----------|--------|------|
| `DATABASE_URL` | `postgresql://postgres:password@postgres:5432/futurkawa_db` | Connexion PostgreSQL |
| `MQTT_BROKER` | `mosquitto` | Hôte du broker MQTT |
| `MQTT_TOPIC` | `futurekawa/brazil` | Topic souscrit pour les mesures |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` | *(vide)* | Serveur d'envoi des emails. **Si vide → mode démo (console)** |
| `ALERT_EMAIL_TO` | `responsable.brazil@futurekawa.com` | Destinataire des alertes |

### Backend central (`central-api`)

| Variable | Défaut | Rôle |
|----------|--------|------|
| `BRAZIL_API_URL` | `http://brazil-api:8000` | URL du backend pays Brésil |

### Frontend

| Variable | Rôle |
|----------|------|
| `VITE_API_BASE_URL` | URL de l'API centrale. **Non définie → l'app utilise des données de démonstration (mock).** |

---

## Principaux endpoints API

### Backend pays — `:8000`

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/lots` | Liste des lots |
| `GET` | `/lots/fifo` | Lots triés FIFO (plus anciens d'abord) |
| `POST` | `/lots` | Créer un lot |
| `GET` | `/lots/{id}` | Détail d'un lot |
| `POST` | `/lots/check-expiration` | Vérifier âge / expiration (lève alertes) |
| `GET` | `/mesures` · `/mesures/latest` | Historique / dernière mesure |
| `POST` | `/mesures` | Enregistrer une mesure (+ contrôle alertes) |
| `GET` | `/alerts` · `/alerts/critical` | Alertes |
| `GET` | `/kpis` | Indicateurs consolidés du pays |

### Backend central — `:8001`

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/countries` | Pays connectés |
| `GET` | `/countries/{c}/lots` · `/lots/fifo` · `/mesures` · `/alerts` · `/kpis` | Données d'un pays |
| `GET` | `/countries/{c}/dashboard` | Tableau de bord d'un pays |
| `GET` | `/dashboard` | **Consolidation tous pays** |
| `GET` | `/lots` · `/lots/fifo` · `/alerts` · `/mesures` | Vues globales agrégées |

---

## Tests

La stratégie de test, la typologie et les cas détaillés sont décrits dans le **[dossier technique (DOSSIER_TECHNIQUE.docx)](DOSSIER_TECHNIQUE.docx)**, section « Plans de tests ».

Exemple de test manuel reproductible (lots triés FIFO via l'API centrale) :

```bash
curl -s http://localhost:8001/countries/brazil/lots/fifo | python -m json.tool
```

---

## État d'avancement & limitations connues

| Élément | État | Détail |
|---------|:----:|--------|
| Backend pays Brésil (API + DB + MQTT + alertes + email) | ✅ | Fonctionnel via Docker Compose |
| Backend central (consolidation) | ✅ | Proxy + agrégation des pays |
| Module IoT (ESP32/DHT22 + simulateur) | ✅ | Simulateur opérationnel ; capteur réel via Wokwi |
| Frontend (UI complète) | ✅ | Fonctionne sur **données de démonstration (mock)** |
| Conteneurisation du frontend | ⛔ | `Dockerfile` frontend à fournir (le service `frontend` du compose ne build pas en l'état) |
| Branchement frontend ↔ API réelle | ⛔ | Routes/champs encore divergents ; couche d'adaptation à écrire |
| IoT réel → persistance backend | ⚠️ | Le capteur publie sur `futurekawa_dht` (`temp`/`humidity`) ; le backend écoute `futurekawa/brazil` (`temperature`/`humidite`). À aligner — le simulateur, lui, alimente bien la base |
| Multi-pays (≥ 3) | ⚠️ | Seul le Brésil est actif ; Équateur/Colombie prêts à activer dans `backend-central/app/config.py` |
| CI/CD Jenkins | ⛔ | À ajouter (`Jenkinsfile`) |
| Tests automatisés | ⛔ | Plan défini (dossier technique) ; implémentation à venir |

---

## Documentation associée

- 📐 **[DOSSIER_TECHNIQUE.docx](DOSSIER_TECHNIQUE.docx)** — architecture, conception IoT, plans de tests
- 📖 **[DOCUMENTATION_UTILISATEUR.docx](DOCUMENTATION_UTILISATEUR.docx)** — guide d'utilisation pour les métiers
