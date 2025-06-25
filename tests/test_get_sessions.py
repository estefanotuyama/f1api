from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
meeting_key = 1236 #MONACO 2024

def test_get_sessions_from_key():
    response = client.get(f'/sessions/{meeting_key}')
    assert response.status_code == 200
    data = response.json()

    print(f"Sessions for meeting key: {meeting_key}")
    for session in data:
        print(f"Session Key: {session['session_key']} Session: {session['location']} {session['session_type']} -> {session['session_name']} {session['date']}")