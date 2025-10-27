import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json
import sys
import os

# Ajouter le répertoire parent au path pour importer main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_health_endpoint_status_code():
    """Test que l'endpoint health retourne un status code 200"""
    response = client.get("/health")
    assert response.status_code == 200

def test_health_endpoint_content_type():
    """Test que l'endpoint health retourne du JSON"""
    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"

def test_health_endpoint_response_structure():
    """Test que la réponse contient les champs requis"""
    response = client.get("/health")
    data = response.json()
    
    # Vérifier que tous les champs requis sont présents
    assert "status" in data
    assert "service" in data
    assert "timestamp" in data

def test_health_endpoint_response_values():
    """Test que les valeurs de la réponse sont correctes"""
    response = client.get("/health")
    data = response.json()
    
    # Vérifier les valeurs
    assert data["status"] == "ok"
    assert data["service"] == "lastmetro-api"
    
    # Vérifier que le timestamp est valide et récent
    timestamp_str = data["timestamp"]
    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    now = datetime.now()
    
    # Le timestamp doit être récent (moins de 5 secondes)
    time_diff = abs((now - timestamp).total_seconds())
    assert time_diff < 5

def test_health_endpoint_multiple_calls():
    """Test que l'endpoint health fonctionne sur plusieurs appels"""
    for _ in range(3):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

def test_health_endpoint_response_format():
    """Test que la réponse est un JSON valide"""
    response = client.get("/health")
    
    # Vérifier que la réponse peut être parsée en JSON
    try:
        json.loads(response.text)
    except json.JSONDecodeError:
        pytest.fail("La réponse n'est pas un JSON valide")

def test_health_endpoint_timestamp_format():
    """Test que le timestamp est au format ISO"""
    response = client.get("/health")
    data = response.json()
    timestamp_str = data["timestamp"]
    
    # Vérifier que le timestamp peut être parsé en datetime
    try:
        datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        pytest.fail(f"Le timestamp '{timestamp_str}' n'est pas au format ISO valide")