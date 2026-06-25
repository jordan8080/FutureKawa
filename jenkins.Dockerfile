# Image Jenkins outillée pour la pipeline FutureKawa : ajoute le client Docker
# et le plugin Docker Compose v2 (`docker compose build`).
# Build :  docker build -t futurekawa-jenkins -f jenkins.Dockerfile .
# Voir CI_CD.md pour le `docker run` (montage du socket Docker de l'hôte).
FROM jenkins/jenkins:lts

USER root
RUN apt-get update \
 && apt-get install -y docker.io docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*
USER jenkins
