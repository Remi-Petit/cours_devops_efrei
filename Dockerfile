# 1. On part d'une image Node.js officielle (version Alpine = légère)
FROM node:18-alpine

# 2. Créer un dossier de travail dans le conteneur
WORKDIR /app

# 3. Copier package.json et package-lock.json EN PREMIER
# (pour profiter du cache Docker lors des rebuilds)
COPY package*.json ./

# 4. Installer SEULEMENT les dépendances de production
RUN npm ci --only=production

# 5. Copier le reste du code
COPY server.js ./

# 6. Exposer le port 3000
EXPOSE 3000

# 7. Variable d'environnement par défaut
ENV PORT=3000

# 8. Commande pour démarrer l'app
CMD ["node", "server.js"]