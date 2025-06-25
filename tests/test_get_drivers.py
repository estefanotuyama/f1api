from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
session_key = 9519 # MONACO 2024 QUALIFYING SESSION

def test_get_drivers_in_session():
    response = client.get(f"/drivers/{session_key}")
    assert response.status_code == 200
    data = response.json()
    print(f"Drivers in session {session_key}: ")
    for driver in data:
        print(f"Name: {driver['first_name']} {driver['last_name']} -> Number: {driver['number']} -> Team: {driver['team']}")