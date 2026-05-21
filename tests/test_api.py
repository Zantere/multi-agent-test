from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_serves_html():
    response = client.get("/")

    assert response.status_code == 200
    assert "AI Dungeon Map Explorer" in response.text


def test_static_assets_are_served():
    response = client.get("/static/app.js")

    assert response.status_code == 200
    assert "generateDungeon" in response.text


def test_dungeon_endpoint_returns_expected_shape():
    response = client.get("/api/dungeon?seed=42&rooms=12")

    assert response.status_code == 200
    data = response.json()
    assert data["seed"] == 42
    assert data["room_count"] == 12
    assert data["start_room_id"] == "0,0"
    assert len(data["rooms"]) == 12
    assert {"id", "x", "y", "name", "description", "exits", "encounter"} <= set(data["rooms"][0])


def test_dungeon_endpoint_rejects_out_of_range_room_counts():
    response = client.get("/api/dungeon?rooms=100")

    assert response.status_code == 422
