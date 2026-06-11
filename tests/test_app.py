def test_docs_load(client):
    response = client.get("/docs")

    assert response.status_code == 200
