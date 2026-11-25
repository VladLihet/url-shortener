def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_link(client):
    response = client.post("/links", json={"url": "https://github.com"})

    assert response.status_code == 201
    body = response.json()
    assert len(body["code"]) == 7
    assert body["short_url"].endswith(body["code"])


def test_create_link_reject_invalid_url(client):
    response = client.post("/links", json={"url": "hello"})

    assert response.status_code == 422


def test_redirect(client):
    response = client.post("/links", json={"url": "https://www.youtube.com/"})
    body = response.json()
    code = body["code"]

    response = client.get(f"/{code}", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://www.youtube.com/"


def test_redirect_unknown_code(client):
    response = client.get("/doesnotexist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Link not found"}


def test_stats_counts_clicks(client):
    response = client.post("/links", json={"url": "https://www.youtube.com/"})
    code = response.json()["code"]

    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)

    response = client.get(f"/links/{code}/stats")

    assert response.status_code == 200
    assert response.json()["clicks"] == 2


def test_metrics_endpoint(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_request_duration_seconds" in response.text
    assert "http_requests_total" in response.text


def test_create_link_gives_up_after_collisions(client, monkeypatch):
    monkeypatch.setattr("app.main.generate_code", lambda: "SAMECODE")

    first = client.post("/links", json={"url": "https://github.com"})
    assert first.status_code == 201

    second = client.post("/links", json={"url": "https://github.com"})
    assert second.status_code == 500
    assert second.json() == {"detail": "Could not generate a unique code"}
