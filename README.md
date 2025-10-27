## Créer un env python :
python -m venv env

## Activer l'env :
env/Scripts/activate

## Quitter l'env :
deactivate

## Lancer FastAPI :
fastapi dev .\main.py --port 8200
uvicorn main:app --host 0.0.0.0 --port 8300 --reload

## Alembic sert à synchroniser la BDD avec le fichier models.
Initialiser Alembic :
alembic init migrations


## Générer une migration :
alembic revision --autogenerate -m "init schema"
alembic upgrade head


## Faire un fichier de requirements :
pip freeze > requirements.txt

## Installer les requirements :
pip install --no-cache-dir -r requirements.txt