from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_events_by_year():
    response = client.get("/events/2024")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("meeting_key" in event for event in data)

    print("2024 Events:")
    for event in data:
        print(f"{event['meeting_official_name']} -> Meeting Key: {event['meeting_key']}")