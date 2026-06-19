# FutureKawa — Backend distribué (café / IoT)

Backend complet conçu pour s'adapter **à 100 %** au frontend React existant (`frontend/`),
sans modifier sa logique (seule la configuration réseau a été ajoutée).

Plateforme de suivi des stocks de café : surveillance IoT température/humidité,
alertes automatiques, tri FIFO, multi-pays (Brésil, Équateur, Colombie).

## Architecture

```
                     ┌──────────────┐
  Navigateur ──────► │   frontend   │  (nginx, build Vite)   :8082
                     │  proxy /api ─┼──────────────┐
                     └──────────────┘              ▼
                                          ┌──────────────┐
                                          │   central    │  (FastAPI, sans DB)  :8001
                                          │  consolide   │
                                          └──────┬───────┘
                         ┌───────────────────────┼───────────────────────┐
                         ▼                        ▼                       ▼
                 ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
                 │ backend pays │        │ backend pays │        │ backend pays │
                 │   brazil     │        │   ecuador    │        │   colombia   │  :8011/8012/8013
                 └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
                        │ (une même image, paramétrée par COUNTRY)      │
        ┌───────────────┴───────────────────────┴───────────────────────┘
        ▼                                   ▲
  ┌──────────┐   measurements (MQTT)   ┌──────────┐        ┌──────────────┐
  │ postgres │◄──────────────────────  │mosquitto │◄────── │ iot-simulator│ (ESP32+DHT22 simulé)
  │ 3 bases  │                         │  :1883   │        └──────────────┘
  └──────────┘                         └────┬─────┘
                                            │ (s'abonne aussi)
                                       ┌────▼─────┐
                                       │ node-red │  alerting parallèle → email/log   :1880
                                       └──────────┘
```

- **Backend pays** : une seule image (`backend/backend-country/`) lancée 3 fois, paramétrée par
  `COUNTRY`. Chaque instance a **sa base** PostgreSQL et écoute le broker MQTT. Contient la
  logique métier, le tri FIFO, les règles d'alerte, l'envoi d'email.
- **Backend central** (`backend/backend-central/`) : **sans base**, interroge les 3 pays en HTTP
  et consolide. C'est le **seul** service exposé au front. Toutes les routes sont préfixées `/api`.
- **Init bases** (`backend/db/`) : crée les 3 bases PostgreSQL au premier démarrage.
- **Simulateur IoT** (`iot-simulator/`) : publie temp/humidité en MQTT pour les 6 entrepôts.
  Mode `normal` (dans les seuils) ou `anomalies` (dépassements → alertes).
- **Node-RED** (`node-red/`) : alerting parallèle, indépendant du backend (voir plus bas).
- **Front** (`frontend/`) : appelle `/api/...` en **same-origin** ; nginx (prod) / Vite (dev)
  proxifient vers le central. Aucune modification de la logique JS.

### Organisation des dossiers
```
g/
├── backend/        backend-country/  ·  backend-central/  ·  db/
├── iot-simulator/  (capteurs ESP32+DHT22 simulés)
├── node-red/       (alerting MQTT → email/log)
├── frontend/       (React + Vite, servi par nginx)
├── mosquitto/      (broker MQTT — infra partagée)
└── docker-compose.yml
```

## Lancement (une commande)

```bash
cd g
cp .env.example .env        # optionnel (valeurs par défaut OK, mode email démo console)
docker compose up --build
```

| Service        | URL / port hôte                          |
|----------------|------------------------------------------|
| **Dashboard**  | **http://localhost:8082**                |
| API centrale (Swagger) | http://localhost:8001/docs       |
| Backend Brésil (Swagger)   | http://localhost:8011/docs   |
| Backend Équateur (Swagger) | http://localhost:8012/docs   |
| Backend Colombie (Swagger) | http://localhost:8013/docs   |
| **Node-RED (alerting)** | **http://localhost:1880**           |
| PostgreSQL     | localhost:5432 (user/pass `futurekawa`)  |
| MQTT (Mosquitto) | localhost:1883                         |

> Si le port 8082 est pris, changez `FRONTEND_ORIGIN` dans `.env` **et** le mapping de ports
> du service `frontend` (les deux doivent correspondre, car l'URL est figée au build Vite).

## Seuils par pays (idéal ± tolérance)

| Pays | Température | Humidité |
|------|-----------|----------|
| Brésil 🇧🇷 | 29 °C ±3 (26–32) | 55 % ±2 (53–57) |
| Équateur 🇪🇨 | 31 °C ±3 (28–34) | 60 % ±2 (58–62) |
| Colombie 🇨🇴 | 26 °C ±3 (23–29) | 80 % ±2 (78–82) |

## Règles métier

- **FIFO** : lots triés par date de stockage (plus anciens d'abord).
- **Alertes auto** : température/humidité hors seuil, lot > 365 j (périmé), lot proche
  expiration (≥ 330 j). Types alignés sur le front : `temperature`, `humidity`, `lot_age`.
- **Anti-duplication** : une seule alerte active par cause (`dedup_key`).
- **Email** au responsable pays à chaque nouvelle alerte (**mode démo console** si SMTP non
  configuré dans `.env`).
- **Statuts de lot** : `conforme`, `alerte`, `perime`, `expedie` (recalculés selon les conditions).

## Démo des alertes IoT

```bash
# Génère des dépassements de seuil en direct (nouvelles alertes temp/humidité)
SIM_MODE=anomalies docker compose up -d --force-recreate iot-simulator
# Retour au mode normal
docker compose up -d --force-recreate iot-simulator
```

## Node-RED — alerting parallèle (indépendant du backend)

Module d'alerting additionnel (cahier des charges), **séparé** du backend FastAPI et de son
`email_service` (qui continue de fonctionner de son côté). Node-RED s'abonne au **même broker
MQTT**, détecte les anomalies et envoie un email (ou logue en console si SMTP non configuré).

- **Interface** : http://localhost:1880 → onglet *« FutureKawa — Alerting »*.
- **Flux** : `mqtt in` (`futurekawa/+/+/measurement`) → *Détection seuils* (par pays, lus depuis
  le topic) → *Email ou log* → nœud **email** si `SMTP_HOST` est défini, sinon nœud **debug**
  (repli console).
- Seuils : Brésil 26–32 °C / 53–57 %, Équateur 28–34 / 58–62, Colombie 23–29 / 78–82.
- Le flux est pré-chargé via l'image et persisté dans le volume `nodered_data` (les
  modifications faites dans l'UI sont conservées). Pour repartir du flux d'origine après
  l'avoir modifié : `docker volume rm futurekawa_nodered_data`.

**Tester (voir une alerte partir) :**
```bash
# 1) Générer des dépassements de seuil
SIM_MODE=anomalies docker compose up -d --force-recreate iot-simulator
# 2) Observer les alertes Node-RED (mode repli console, SMTP non configuré)
docker compose logs -f node-red        # lignes "email simulé: …Anomalie…"
#    ou, dans l'UI http://localhost:1880, ouvrir le panneau "Debug" (à droite)
# 3) Revenir au mode normal
docker compose up -d --force-recreate iot-simulator
```
Avec un vrai SMTP (renseigner `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM`, `SMTP_TO` dans `.env`),
le même message est envoyé par email au lieu d'être logué. *(Auth SMTP : si le serveur exige
identifiants, saisissez-les dans le nœud email de l'UI puis « Deploy ».)*

## Configuration email (optionnelle)

Renseigner dans `.env` : `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`,
`SMTP_USE_TLS`. Sans configuration, les emails s'affichent dans les logs (`docker compose logs backend-brazil`).

## Développement front (hors Docker)

```bash
docker compose up -d   # backends seuls
cd frontend && npm install && npm run dev   # Vite :5173, proxy /api -> :8001
```

## Données live & rafraîchissement automatique

- Le **simulateur** publie de nouvelles mesures toutes les ~10 s (MQTT) ; chaque backend pays
  les stocke et met à jour `currentTemp`/`currentHumidity` de l'entrepôt.
- Le **front** rafraîchit automatiquement (polling 8 s) le Dashboard, la page Pays (jauges
  temp/humidité) et le détail d'un lot (graphe capteurs) — **sans recharger la page**.

## CRUD disponible

| Entité | Créer | Supprimer | UI |
|--------|-------|-----------|-----|
| **Lot** | `POST /api/lots` | `DELETE /api/lots/{id}` | Page Pays (« + Lot » / 🗑) |
| **Entrepôt** | `POST /api/warehouses` | `DELETE /api/warehouses/{id}` * | Page Pays (« + Entrepôt » / ✕) |
| **Pays** | `POST /api/countries` ** | `DELETE /api/countries/{id}` | Dashboard (« Registre des pays ») |

\* Suppression d'entrepôt refusée s'il contient des lots (message explicite).
\** **Limite** : ajouter un pays n'écrit que dans le **registre du central** (routage). Ça
n'instancie **pas** de backend/base/broker : l'`url` doit pointer vers un backend pays déjà
déployé. La suppression retire le pays du routage (sa base reste intacte).

## Vérifier que les données sont dynamiques (pas de mock)

```bash
# 1) Les mesures changent dans le temps (lancer deux fois à ~10 s d'intervalle) :
curl -s http://localhost:8001/api/sensors/current
# 2) Données réelles via le proxy nginx du front :
curl -s http://localhost:8082/api/lots
# 3) Front : la base URL est bakée dans le bundle (jamais de mock) :
curl -s http://localhost:8082/ | grep -o '/assets/index-[^"]*\.js'   # puis grep 8082 dans le .js
# 4) CRUD de bout en bout : créer/supprimer un lot ou un entrepôt depuis la page Pays.
```

## Contrat d'API (exposé par le central, préfixe `/api`)

Lots : `GET /api/lots`, `GET /api/countries/{c}/lots`, `GET /api/warehouses/{id}/lots`,
`GET /api/lots/{id}`, `POST /api/lots`, `PATCH /api/lots/{id}/status`, `DELETE /api/lots/{id}` ·
Capteurs : `GET /api/warehouses/{id}/sensors?limit=N`, `GET /api/countries/{c}/sensors/latest`,
`GET /api/sensors/current` ·
Alertes : `GET /api/alerts?country=&type=&status=`, `POST /api/alerts/{id}/resolve`,
`GET /api/alerts/count` ·
Entrepôts : `GET /api/warehouses`, `POST /api/warehouses`, `GET /api/countries/{c}/warehouses`,
`GET /api/warehouses/{id}`, `DELETE /api/warehouses/{id}` ·
Pays / consolidation : `GET /api/countries`, `POST /api/countries`, `DELETE /api/countries/{id}`,
`GET /api/dashboard`, `GET /api/countries/{c}/kpis`, `GET /api/countries/{c}/fifo`.
