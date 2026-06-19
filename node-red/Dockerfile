FROM nodered/node-red:4.0

# Le nœud email n'est pas inclus dans l'image officielle : on l'ajoute.
RUN npm install node-red-node-email

# Flux pré-configuré (copié dans le volume /data au premier démarrage).
COPY --chown=node-red:node-red flows.json /data/flows.json
