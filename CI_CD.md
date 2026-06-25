# CI/CD — Pipeline Jenkins FutureKawa

Ce document décrit la chaîne d'intégration continue du projet : tests automatisés
(pytest), analyse qualité (ruff), build et packaging des images Docker, orchestrés
par une pipeline **Jenkins déclarative** ([`Jenkinsfile`](Jenkinsfile)).

## 1. Vue d'ensemble de la pipeline

Les stages s'exécutent dans l'ordre ; **toute erreur arrête la pipeline** et la marque
en échec.

| Stage      | Rôle                                                                    |
|------------|-------------------------------------------------------------------------|
| Checkout   | Récupère le code depuis Git.                                            |
| Build      | `docker compose build` des images (backend pays, central, frontend).    |
| Test       | Exécute pytest dans un conteneur, produit un rapport **JUnit XML**.     |
| Qualité    | Linter Python `ruff` (équivalent flake8) sur le backend.                |
| Package    | Tag des images Docker (`<service>:<BUILD_NUMBER>` + `:latest`).         |

En fin de pipeline (`post { always }`), le rapport de tests est **publié** dans l'UI
Jenkins **et archivé** comme artefact téléchargeable.

---

## 2. Lancer Jenkins en local via Docker

Jenkins a besoin d'accéder au démon Docker (la pipeline construit des images). On
monte donc le socket Docker de l'hôte dans le conteneur Jenkins, et on ajoute le
client Docker + le plugin compose.

### 2.1 Construire une image Jenkins outillée Docker

Créez `jenkins.Dockerfile` (ou utilisez celui-ci à la racine) :

```dockerfile
FROM jenkins/jenkins:lts
USER root
# Client Docker + plugin compose v2 (pour `docker compose build`).
RUN apt-get update \
 && apt-get install -y docker.io docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*
USER jenkins
```

Build de l'image :

```bash
docker build -t futurekawa-jenkins -f jenkins.Dockerfile .
```

### 2.2 Démarrer le conteneur Jenkins

> Sur **Docker Desktop (Windows/Mac)** comme sous **Linux**, le montage du socket
> `/var/run/docker.sock` donne au conteneur Jenkins l'accès au démon de l'hôte.
> Le `-u root` simplifie l'accès au socket pour une démo locale.

```bash
docker run -d --name jenkins -u root \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  futurekawa-jenkins
```

Récupérez le mot de passe d'installation initial :

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Ouvrez http://localhost:8080, collez ce mot de passe, installez les **plugins
suggérés**, puis créez votre compte admin.

> Vérifiez ensuite que Docker est accessible depuis Jenkins :
> `docker exec jenkins docker version` doit afficher client **et** serveur.

---

## 3. Créer le job (pipeline) pointant sur le dépôt Git

1. Tableau de bord Jenkins → **New Item**.
2. Nom : `futurekawa-ci`, type : **Pipeline**, → **OK**.
3. Section **Pipeline** :
   - *Definition* : **Pipeline script from SCM**
   - *SCM* : **Git**
   - *Repository URL* : l'URL de votre dépôt (ex. `https://github.com/<vous>/projetMSPR.git`)
   - *Credentials* : ajoutez-les si le dépôt est privé.
   - *Branch Specifier* : `*/main` (ou votre branche, ex. `*/merge-backend-frontend-node-red`)
   - *Script Path* : `Jenkinsfile` (déjà à la racine)
4. **Save**.

> Optionnel — déclenchement automatique : cochez **Poll SCM** (`H/5 * * * *`) ou
> configurez un **webhook** GitHub vers `http://<jenkins>/github-webhook/`.

---

## 4. Déclencher la pipeline et trouver la « preuve d'exécution »

### Déclencher

- Ouvrez le job `futurekawa-ci` → **Build Now**.
- Suivez l'exécution en direct via **Stage View** (vue par stage) ou **Console Output**.

### Où se trouve la preuve pour le jury

| Preuve                          | Où la trouver dans Jenkins                                          |
|---------------------------------|---------------------------------------------------------------------|
| Logs détaillés par stage        | Build → **Console Output** (horodaté) et **Pipeline Steps**.        |
| Résultats des tests             | Build → **Test Result** (nombre de tests, passés/échoués, durée).   |
| Rapport JUnit (fichier)         | Build → **Artifacts** → `backend/backend-country/reports/junit.xml`.|
| Tendance des tests              | Page du job → graphe **Test Result Trend**.                         |
| Images Docker produites         | Stage **Package** dans la console (`docker images | grep futurekawa`).|

Un build **vert** = build + tests + qualité + package OK. Un build **rouge** indique
le stage fautif (ex. un test cassé fait échouer le stage *Test*).

---

## 5. Lancer les tests manuellement (sans Jenkins)

### 5.1 En local avec un environnement Python

Prérequis : **Python 3.12** installé.

```bash
cd backend/backend-country

# 1. Environnement virtuel isolé
python -m venv .venv
# Windows (PowerShell) :
.\.venv\Scripts\Activate.ps1
# Linux/Mac :
# source .venv/bin/activate

# 2. Dépendances (prod + dev)
pip install -r requirements.txt -r requirements-dev.txt

# 3. Lancer les tests
pytest
```

`pytest` lit [`pytest.ini`](backend/backend-country/pytest.ini) et génère
`reports/junit.xml`. Les tests utilisent une base **SQLite en mémoire** isolée :
ils ne touchent **jamais** à PostgreSQL ni aux données réelles.

Linter qualité, à la demande :

```bash
ruff check .
```

### 5.2 Sans rien installer (via Docker, comme la pipeline)

```bash
cd backend/backend-country
docker build -t futurekawa-backend-test -f Dockerfile.test .
docker run --rm futurekawa-backend-test          # exécute pytest
docker run --rm futurekawa-backend-test ruff check .   # exécute le linter
```

---

## 6. Périmètre des tests

| Fichier                                   | Type            | Couvre                                                        |
|-------------------------------------------|-----------------|---------------------------------------------------------------|
| `tests/test_alerts.py`                    | Unitaire        | Moteur d'alertes : seuils T°/humidité, règle d'âge > 365 j, anti-duplication. |
| `tests/test_fifo.py`                      | Unitaire        | Tri FIFO des lots (plus ancien d'abord, exclusion des expédiés). |
| `tests/test_api.py`                       | API / intégration | Routes : santé, lots (lister/créer/supprimer), mesures, alertes. |

Total : **26 tests**, base de test isolée (SQLite en mémoire), aucun envoi email réel
(mode console).
