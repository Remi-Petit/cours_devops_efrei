## Créer un env python :
* python -m venv env

## Activer l'env :
* env/Scripts/activate

## Quitter l'env :
* deactivate

# Lancer FastAPI :
* uvicorn main:app --host 0.0.0.0 --port 8300 --reload

# Installer les requirements :
* pip install --no-cache-dir -r requirements.txt

## Faire un fichier de requirements :
* pip freeze > requirements.txt