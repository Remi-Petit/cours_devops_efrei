import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json
import sys
import os

# Ajouter le répertoire parent au path pour importer main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_next_metro_endpoint_with_valid_station():
    """Test que l'endpoint next-metro fonctionne avec une station valide"""
    response = client.get("/next-metro?station=Chatelet")
    assert response.status_code == 200

def test_next_metro_endpoint_content_type():
    """Test que l'endpoint next-metro retourne du JSON"""
    response = client.get("/next-metro?station=Chatelet")
    assert response.headers["content-type"] == "application/json"

def test_next_metro_endpoint_response_structure():
    """Test que la réponse contient les champs requis"""
    response = client.get("/next-metro?station=Chatelet")
    data = response.json()
    
    # Vérifier que tous les champs requis sont présents
    assert "station" in data
    assert "line" in data
    assert "nextArrival" in data
    assert "headwayMin" in data

def test_next_metro_endpoint_response_values():
    """Test que les valeurs de la réponse sont correctes"""
    station_name = "Chatelet"
    response = client.get(f"/next-metro?station={station_name}")
    data = response.json()
    
    # Vérifier les valeurs
    assert data["station"] == station_name
    assert data["line"] == "M1"
    assert data["headwayMin"] == 5
    
    # Vérifier le format de l'heure (HH:MM)
    next_arrival = data["nextArrival"]
    assert len(next_arrival) == 5
    assert next_arrival[2] == ":"
    
    # Vérifier que c'est une heure valide
    try:
        hours, minutes = next_arrival.split(":")
        hours_int = int(hours)
        minutes_int = int(minutes)
        assert 0 <= hours_int <= 23
        assert 0 <= minutes_int <= 59
    except ValueError:
        pytest.fail(f"Format d'heure invalide: {next_arrival}")

def test_next_metro_endpoint_time_calculation():
    """Test que l'heure calculée est environ 5 minutes dans le futur"""
    response = client.get("/next-metro?station=Chatelet")
    data = response.json()
    
    next_arrival_str = data["nextArrival"]
    hours, minutes = next_arrival_str.split(":")
    
    # Calculer l'heure attendue (maintenant + 5 minutes)
    now = datetime.now()
    expected_time = now + timedelta(minutes=5)
    expected_str = expected_time.strftime("%H:%M")
    
    # L'heure retournée doit être proche de l'heure attendue (tolérance de 1 minute)
    actual_time = datetime.strptime(next_arrival_str, "%H:%M").time()
    expected_time_obj = datetime.strptime(expected_str, "%H:%M").time()
    
    # Convertir en minutes pour comparaison
    actual_minutes = actual_time.hour * 60 + actual_time.minute
    expected_minutes = expected_time_obj.hour * 60 + expected_time_obj.minute
    
    # Tolérance de 1 minute
    assert abs(actual_minutes - expected_minutes) <= 1

def test_next_metro_endpoint_missing_station_parameter():
    """Test que l'endpoint retourne une erreur 400 sans paramètre station"""
    response = client.get("/next-metro")
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "missing station parameter"

def test_next_metro_endpoint_empty_station_parameter():
    """Test que l'endpoint retourne une erreur 400 avec un paramètre station vide"""
    response = client.get("/next-metro?station=")
    assert response.status_code == 400
    
    data = response.json()
    assert data["detail"] == "missing station parameter"

def test_next_metro_endpoint_multiple_stations():
    """Test que l'endpoint fonctionne avec différentes stations"""
    stations = ["Chatelet", "Republique", "Bastille", "Nation"]
    
    for station in stations:
        response = client.get(f"/next-metro?station={station}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["station"] == station
        assert data["line"] == "M1"
        assert data["headwayMin"] == 5

def test_next_metro_endpoint_station_with_spaces():
    """Test que l'endpoint fonctionne avec des stations contenant des espaces"""
    station_name = "Champs Elysees"
    response = client.get(f"/next-metro?station={station_name}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["station"] == station_name

def test_next_metro_endpoint_special_characters():
    """Test que l'endpoint fonctionne avec des caractères spéciaux"""
    station_name = "Château-Rouge"
    response = client.get(f"/next-metro?station={station_name}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["station"] == station_name

def test_next_metro_endpoint_response_format():
    """Test que la réponse est un JSON valide"""
    response = client.get("/next-metro?station=Chatelet")
    
    # Vérifier que la réponse peut être parsée en JSON
    try:
        json.loads(response.text)
    except json.JSONDecodeError:
        pytest.fail("La réponse n'est pas un JSON valide")

def test_next_metro_endpoint_multiple_calls_consistency():
    """Test que l'endpoint est cohérent sur plusieurs appels"""
    station_name = "Chatelet"
    
    for _ in range(3):
        response = client.get(f"/next-metro?station={station_name}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["station"] == station_name
        assert data["line"] == "M1"
        assert data["headwayMin"] == 5
        assert len(data["nextArrival"]) == 5
        assert ":" in data["nextArrival"]