# Guide utilisateur — FutureKawa

Plateforme de suivi des stocks de café avec surveillance IoT (température / humidité),
alertes automatiques, tri FIFO et pilotage multi-pays (**Brésil 🇧🇷, Équateur 🇪🇨, Colombie 🇨🇴**).

Ce document s'adresse aux **utilisateurs** de la plateforme (responsables qualité, gestionnaires
d'entrepôts, opérateurs) ainsi qu'aux personnes chargées de la **mettre en route** pour une démo.

---

## Table des matières

1. [À quoi sert FutureKawa](#1-à-quoi-sert-futurekawa)
2. [Vue d'ensemble du système](#2-vue-densemble-du-système)
3. [Démarrer la plateforme](#3-démarrer-la-plateforme)
4. [Accéder aux interfaces](#4-accéder-aux-interfaces)
5. [Utiliser l'application web](#5-utiliser-lapplication-web)
   - [Le tableau de bord](#51-le-tableau-de-bord)
   - [La page d'un pays](#52-la-page-dun-pays)
   - [Le détail d'un entrepôt](#53-le-détail-dun-entrepôt)
   - [Le détail d'un lot](#54-le-détail-dun-lot)
   - [La page Alertes](#55-la-page-alertes)
6. [Comprendre les conditions et les seuils](#6-comprendre-les-conditions-et-les-seuils)
7. [Comprendre les alertes](#7-comprendre-les-alertes)
8. [Gérer les données (créer / supprimer)](#8-gérer-les-données-créer--supprimer)
9. [Le temps réel : comment ça se met à jour](#9-le-temps-réel-comment-ça-se-met-à-jour)
10. [Faire une démonstration d'anomalies](#10-faire-une-démonstration-danomalies)
11. [Alerting par e-mail (Node-RED + backend)](#11-alerting-par-e-mail-node-red--backend)
12. [Foire aux questions / dépannage](#12-foire-aux-questions--dépannage)
13. [Glossaire](#13-glossaire)

---

## 1. À quoi sert FutureKawa

FutureKawa permet de **surveiller en continu les conditions de stockage du café** dans plusieurs
pays producteurs et de **réagir vite** quand quelque chose dérape.

Concrètement, la plateforme vous aide à :

- **Suivre la température et l'humidité** de chaque entrepôt, en temps quasi réel ;
- **Être alerté automatiquement** quand un entrepôt sort des plages acceptables ou qu'un lot
  devient trop vieux ;
- **Gérer le stock** (lots, entrepôts) avec un tri **FIFO** (les lots les plus anciens d'abord) ;
- **Consolider la vue** des trois pays sur un seul tableau de bord.

---

## 2. Vue d'ensemble du système

Vous n'avez pas besoin de connaître la technique pour utiliser la plateforme, mais voici le
principe général :

```
   Capteurs (simulés)              Surveillance                 Vous
   ┌──────────────┐    mesures    ┌──────────────┐   web      ┌──────────┐
   │ iot-simulator│ ─────────────►│  Backends    │ ──────────►│ Dashboard│
   │ (ESP32+DHT22)│   (MQTT)      │  par pays    │  (HTTP)    │  (React) │
   └──────────────┘               │  + central   │            └──────────┘
                                   └──────┬───────┘
                                          │ alertes
                                   ┌──────▼───────┐
                                   │   E-mail /   │
                                   │  Node-RED    │
                                   └──────────────┘
```

- **Capteurs** : des capteurs température/humidité (ici simulés) publient des mesures en continu.
- **Backends pays** : un service par pays reçoit les mesures, les enregistre, calcule les statuts
  et **déclenche les alertes**.
- **Backend central** : regroupe les données des trois pays pour l'affichage.
- **Application web (Dashboard)** : ce que vous utilisez au quotidien.
- **Alerting e-mail** : envoi d'un message au responsable du pays à chaque nouvelle alerte.

---

## 3. Démarrer la plateforme

> Pré-requis : **Docker** et **Docker Compose** installés.

Depuis le dossier du projet :

```bash
docker compose up --build
```

La première fois, l'image se construit et les **bases de données sont peuplées automatiquement**
avec des données de démonstration (entrepôts, lots, historique de mesures). Patientez jusqu'à ce
que tous les services soient « healthy ».

Pour **tout réinitialiser** (repartir d'une base vierge et re-générer les données de démo) :

```bash
docker compose down -v      # -v supprime les volumes (les bases)
docker compose up --build
```

Pour **arrêter** sans effacer les données :

```bash
docker compose down
```

---

## 4. Accéder aux interfaces

| Interface | Adresse | À quoi ça sert |
|---|---|---|
| **Application web (Dashboard)** | **http://localhost:8082** | Interface principale — c'est ici que vous travaillez |
| Node-RED (alerting) | http://localhost:1880 | Visualiser / configurer l'alerting e-mail |
| API centrale (Swagger) | http://localhost:8001/docs | Documentation technique de l'API |
| Backend Brésil / Équateur / Colombie | 8011 / 8012 / 8013 `/docs` | API d'un pays (technique) |

👉 **Au quotidien, vous n'avez besoin que de http://localhost:8082.**

---

## 5. Utiliser l'application web

### 5.1 Le tableau de bord

Page d'accueil (`http://localhost:8082`). Elle donne la **vue consolidée des trois pays**.

On y trouve :

- **4 indicateurs clés** en haut : nombre de lots en stock, alertes actives, lots périmés,
  taux de conformité.
- **Une carte par pays** : température et humidité moyennes, nombre de lots, % conformes, et un
  **badge d'état** (🟢 conforme / 🟡 en alerte). Cliquez sur une carte pour ouvrir le pays.
- **Les alertes récentes** : les dernières alertes actives, avec lien vers la page Alertes.
- **Le registre des pays** (administration) : liste des pays connus du système.

> Le tableau de bord se **rafraîchit tout seul** toutes les 8 secondes.

### 5.2 La page d'un pays

Accessible en cliquant sur une carte pays, ou via l'URL `/pays/<pays>`.

Vous y voyez :

- **L'en-tête du pays** : seuils idéaux (température / humidité), responsable, nombre d'entrepôts
  et de lots.
- **Les conditions actuelles par entrepôt** : une vignette par entrepôt avec ses jauges
  température/humidité et son badge d'état. Cliquez une vignette pour ouvrir le détail.
- **La liste des lots stockés**, triée **FIFO** (les plus anciens en premier), avec des **filtres**
  par entrepôt et par statut (conforme / en alerte / périmé / expédié).

Depuis cette page, vous pouvez aussi **ajouter un entrepôt** (bouton « + Entrepôt ») et
**ajouter un lot** (bouton « + Lot »). Voir [§8](#8-gérer-les-données-créer--supprimer).

### 5.3 Le détail d'un entrepôt

En cliquant sur une vignette d'entrepôt, vous accédez aux **graphiques des mesures** (température
et humidité sur les derniers jours) et à la **liste des lots** de cet entrepôt.

### 5.4 Le détail d'un lot

Chaque lot a une fiche : identifiant, entrepôt, exploitation, **âge de stockage**, poids, variété
(Arabica / Robusta), grade (Grade 1 / Grade 2 / Specialty), statut, et le graphe des conditions de
son entrepôt. C'est ici que l'on visualise si un lot approche de la limite d'âge.

### 5.5 La page Alertes

Accessible via le menu, ou `/alertes`. Elle centralise **toutes les alertes**.

- **Résumé** : nombre d'alertes actives, critiques, et résolues.
- **Filtres** : par pays, par type (🌡️ température / 💧 humidité / ⏰ lot) et par statut
  (actives / résolues).
- **Liste** séparée entre **alertes actives** et **alertes résolues**.
- **Résoudre une alerte** : bouton sur chaque alerte active (passe l'alerte en « résolue »).

> La page Alertes se **rafraîchit automatiquement** : les nouvelles alertes apparaissent sans
> recharger la page.

---

## 6. Comprendre les conditions et les seuils

Chaque pays a une **plage idéale** de température et d'humidité. En dehors de cette plage, l'entrepôt
passe « en alerte » et une alerte est créée.

| Pays | Température | Humidité |
|------|-----------|----------|
| Brésil 🇧🇷 | 29 °C ± 3 (**26–32**) | 55 % ± 2 (**53–57**) |
| Équateur 🇪🇨 | 31 °C ± 3 (**28–34**) | 60 % ± 2 (**58–62**) |
| Colombie 🇨🇴 | 26 °C ± 3 (**23–29**) | 80 % ± 2 (**78–82**) |

- **Dans la plage** → entrepôt **conforme** (🟢).
- **Hors plage** (température OU humidité) → entrepôt **en alerte** (🟡) + création d'une alerte.

---

## 7. Comprendre les alertes

Une **alerte** est créée automatiquement par le système. Il en existe trois **types** :

| Type | Icône | Déclencheur |
|---|---|---|
| **Température** | 🌡️ | Température de l'entrepôt hors plage |
| **Humidité** | 💧 | Humidité de l'entrepôt hors plage |
| **Lot** (âge) | ⏰ | Lot stocké depuis plus de **365 jours** (périmé) ou **proche de l'expiration** (≥ 330 jours) |

Chaque alerte a un **niveau de gravité**, calculé selon l'ampleur du dépassement :

| Niveau | Indication |
|---|---|
| 🔴 **Critique** | Dépassement important |
| 🟠 **Haute** | Dépassement marqué |
| 🟡 **Moyenne** | Dépassement modéré |
| 🔵 **Faible** | Léger dépassement |

Règles importantes :

- **Anti-duplication** : il n'y a **qu'une seule alerte active par cause** (par entrepôt et par
  type). Tant qu'elle n'est pas résolue, on ne recrée pas la même.
- **E-mail** : à chaque nouvelle alerte, un message est envoyé au **responsable du pays**
  (ou affiché dans les logs si aucun serveur e-mail n'est configuré — mode démo).
- **Statuts de lot** : `conforme`, `alerte`, `perime`, `expedie` — recalculés selon les conditions.
  Un lot `perime` ou `expedie` n'est jamais « rétrogradé ».

---

## 8. Gérer les données (créer / supprimer)

| Action | Où | Comment |
|---|---|---|
| **Ajouter un lot** | Page Pays | Bouton « + Lot », remplir le formulaire |
| **Supprimer un lot** | Page Pays | Icône 🗑 sur la ligne du lot |
| **Ajouter un entrepôt** | Page Pays | Bouton « + Entrepôt » |
| **Supprimer un entrepôt** | Page Pays | Icône ✕ sur la vignette de l'entrepôt |
| **Gérer les pays** | Tableau de bord | Panneau « Registre des pays » |

Points d'attention :

- La suppression d'un **entrepôt** est **refusée s'il contient encore des lots** (un message
  l'explique). Videz/déplacez d'abord les lots.
- **Ajouter un pays** ne fait que l'enregistrer dans le **registre central** (routage) : cela
  **n'instancie pas** un nouveau backend/base. L'URL doit pointer vers un backend pays déjà déployé.

---

## 9. Le temps réel : comment ça se met à jour

- Le **simulateur** publie de nouvelles mesures à intervalle court (quelques secondes).
- Chaque **backend pays** enregistre la mesure, met à jour la température/humidité **courantes** de
  l'entrepôt et **crée une alerte si la mesure est hors seuil**.
- L'**application web** se rafraîchit automatiquement (polling ~8 s) sur :
  - le **tableau de bord** (indicateurs, cartes pays, alertes récentes),
  - la **page Pays** (jauges des entrepôts, statuts),
  - la **page Alertes** (nouvelles alertes en direct),
  - le **détail d'un lot/entrepôt** (graphes).

👉 **Vous n'avez jamais besoin de recharger la page** pour voir les dernières valeurs.

---

## 10. Faire une démonstration d'anomalies

Le simulateur fonctionne en **mode mixte** par défaut : il envoie majoritairement des valeurs
**conformes** avec, de temps en temps, une **anomalie** (dépassement de seuil) qui déclenche une
alerte. C'est idéal pour une démo : on voit alterner conforme / anomalie.

Pour **forcer des anomalies en continu** (stress test) :

```bash
SIM_MODE=anomalies docker compose up -d --force-recreate iot-simulator
```

Pour **revenir au comportement par défaut** (anomalies occasionnelles) :

```bash
SIM_MODE=mixed docker compose up -d --force-recreate iot-simulator
```

Pour **désactiver toute anomalie** (tout reste conforme) :

```bash
SIM_MODE=calm docker compose up -d --force-recreate iot-simulator
```

Variables utiles : `SIM_MODE` (`mixed` / `anomalies` / `calm`), `SIM_INTERVAL` (secondes entre
deux cycles), `SIM_ANOMALY_RATE` (probabilité d'anomalie en mode mixte, ex. `0.25`).

**Observer la chaîne dans les logs :**

```bash
docker compose logs -f iot-simulator     # les mesures publiées (⚠ ANOMALIE marquée)
docker compose logs -f backend-brazil    # réception + création d'alertes côté backend
```

Une anomalie générée par le simulateur est : (a) reçue par le backend, (b) enregistrée comme
alerte, (c) visible sur le front en quelques secondes.

---

## 11. Alerting par e-mail (Node-RED + backend)

Deux mécanismes d'alerte e-mail coexistent :

1. **Le backend pays** envoie un e-mail au responsable à chaque nouvelle alerte.
2. **Node-RED** (http://localhost:1880) fournit un **alerting parallèle, indépendant** : il s'abonne
   au même flux de mesures, détecte les dépassements et envoie un e-mail (ou logue en console si
   aucun SMTP n'est configuré).

**Mode démo (sans serveur e-mail)** : les messages s'affichent dans les logs.

```bash
docker compose logs -f node-red          # lignes « email simulé : …Anomalie… »
docker compose logs -f backend-brazil    # e-mails du backend en mode console
```

**Mode réel** : renseignez dans `.env` : `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`,
`SMTP_FROM`, `SMTP_USE_TLS` (et `SMTP_TO` pour Node-RED). Les e-mails sont alors réellement envoyés.

---

## 12. Foire aux questions / dépannage

**Je ne vois jamais d'anomalie ni d'alerte.**
Vérifiez que le simulateur tourne (`docker compose logs -f iot-simulator`). En mode `mixed`, les
anomalies sont occasionnelles : attendez quelques cycles, ou forcez-les avec `SIM_MODE=anomalies`
(voir [§10](#10-faire-une-démonstration-danomalies)).

**Le tableau de bord est vide / « Pays non trouvé ».**
Les services ne sont peut-être pas encore prêts. Attendez que tout soit « healthy », puis
rechargez. En dernier recours : `docker compose down -v && docker compose up --build`.

**Une alerte ne se recrée pas après résolution.**
Normal tant que la cause persiste : il n'y a **qu'une alerte active par cause**. Une nouvelle alerte
de même type ne réapparaît que si une nouvelle anomalie survient après résolution.

**Le port 8082 est déjà utilisé.**
Modifiez `FRONTEND_ORIGIN` dans `.env` **et** le mapping de ports du service `frontend` dans
`docker-compose.yml` (les deux doivent correspondre, car l'URL est figée au build).

**Je veux repartir des données de démo d'origine.**
`docker compose down -v` puis `docker compose up --build` (le `-v` efface les bases et relance le
peuplement automatique).

**Réinitialiser uniquement Node-RED.**
`docker volume rm futurekawa_nodered_data` puis relancer.

---

## 13. Glossaire

- **Lot** : un ensemble de café stocké, identifié (ex. `FK-BR-SP-001`), avec une date de stockage,
  un poids, une variété et un grade.
- **Entrepôt** : lieu de stockage rattaché à un pays et à une exploitation, avec des conditions
  (température/humidité) suivies par capteurs.
- **Exploitation** : la ferme / propriété d'origine du café (ex. *Fazenda Aurora*).
- **FIFO** (*First In, First Out*) : règle de gestion où les lots les plus anciens sont expédiés en
  priorité.
- **Conforme / En alerte / Périmé / Expédié** : statuts possibles d'un lot.
- **Seuil** : plage idéale de température/humidité par pays ; en dehors, une alerte est créée.
- **MQTT** : protocole par lequel les capteurs publient leurs mesures.
- **Node-RED** : outil d'alerting visuel branché sur le même flux de mesures.
</content>
</invoke>
