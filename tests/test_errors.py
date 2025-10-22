from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_not_found_item():
    """Тест что 404 ошибки возвращают RFC 7807 формат"""
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    # Проверяем формат RFC 7807
    assert "type" in body
    assert "title" in body
    assert "status" in body
    assert "detail" in body
    assert "correlation_id" in body
    assert body["status"] == 404


def test_validation_error():
    """Тест что ошибки валидации возвращают RFC 7807 формат"""
    r = client.post("/items", params={"name": ""})
    assert r.status_code == 422
    body = r.json()
    # Проверяем формат RFC 7807
    assert "type" in body
    assert "title" in body
    assert "status" in body
    assert "detail" in body
    assert "correlation_id" in body
    assert body["status"] == 422


def test_rfc7807_format_consistency():
    """Тест согласованности формата RFC 7807 для разных типов ошибок"""
    # Тестируем 404
    response_404 = client.get("/items/999")
    assert response_404.status_code == 404
    data_404 = response_404.json()

    # Тестируем 422
    response_422 = client.post("/items", params={"name": ""})
    assert response_422.status_code == 422
    data_422 = response_422.json()

    # Оба ответа должны иметь одинаковую структуру
    for data in [data_404, data_422]:
        assert set(data.keys()) == {
            "type",
            "title",
            "status",
            "detail",
            "correlation_id",
        }
        assert isinstance(data["correlation_id"], str)
        assert len(data["correlation_id"]) == 36  # UUID length
