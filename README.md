# Lancer l'app
* npm start

# Exécuter un script SQL spécifique
* docker-compose exec postgres psql -U app -d dernier_metro -f /docker-entrypoint-initdb.d/nouveau_script.sql