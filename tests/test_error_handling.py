import pytest
from fastapi.testclient import TestClient

from app.errors import ProblemDetailException
from app.main import app

client = TestClient(app)


class TestErrorHandling:
    """Тесты для обработки ошибок в формате RFC 7807"""

    def test_problem_detail_exception_format(self):
        """Тест формата ProblemDetailException"""
        with pytest.raises(ProblemDetailException) as exc_info:
            raise ProblemDetailException(
                status_code=400,
                title="Bad Request",
                detail="Invalid input data",
                error_type="/errors/validation",
            )

        exception = exc_info.value
        assert exception.status_code == 400
        assert exception.title == "Bad Request"
        assert exception.detail == "Invalid input data"
        assert exception.error_type == "/errors/validation"

    def test_validation_error_returns_rfc7807_format(self):
        """Тест что ошибки валидации возвращают RFC 7807 формат"""
        response = client.post("/items", params={"name": ""})

        assert response.status_code == 422
        assert response.headers["content-type"] == "application/problem+json"

        data = response.json()
        assert data["type"] == "/errors/validation"
        assert data["title"] == "Validation Error"
        assert data["status"] == 422
        assert "correlation_id" in data
        assert len(data["correlation_id"]) == 36  # UUID v4 length

    def test_not_found_returns_rfc7807_format(self):
        """Тест что 404 ошибки возвращают RFC 7807 формат"""
        response = client.get("/items/9999")

        assert response.status_code == 404
        assert response.headers["content-type"] == "application/problem+json"

        data = response.json()
        assert data["type"] == "/errors/not-found"
        assert data["title"] == "Not Found"
        assert data["status"] == 404
        assert "item not found" in data["detail"]
        assert "correlation_id" in data

    #    def test_generic_exception_handling(self):
    #        """Тест обработки неожиданных исключений"""
    #        # Создаем временный endpoint для тестирования
    #        from fastapi import FastAPI
    #        from app.errors import generic_exception_handler
    #
    #        test_app = FastAPI()
    #
    #        @test_app.get("/test-error")
    #        def test_error():
    #            raise ValueError("Test unexpected error")
    #
    #        test_app.add_exception_handler(Exception, generic_exception_handler)
    #
    #        test_client = TestClient(test_app)
    #        response = test_client.get("/test-error")
    #
    #        assert response.status_code == 500
    #        assert response.headers["content-type"] == "application/problem+json"
    #
    #        data = response.json()
    #        assert data["type"] == "about:blank"
    #        assert data["title"] == "Internal Server Error"
    #        assert data["status"] == 500
    #        assert "correlation_id" in data

    def test_different_error_types_have_different_formats(self):
        """Тест что разные типы ошибок имеют разные форматы"""
        # Тестируем 400 ошибку
        response_400 = client.post(
            "/items", params={"name": "a" * 101}
        )  # Слишком длинное имя

        # Тестируем 404 ошибку
        response_404 = client.get("/items/9999")

        # Проверяем что обе ошибки имеют корректный формат
        for response in [response_400, response_404]:
            data = response.json()
            assert "type" in data
            assert "title" in data
            assert "status" in data
            assert "detail" in data
            assert "correlation_id" in data
            assert response.headers["content-type"] == "application/problem+json"


class TestInputValidation:
    """Тесты для валидации входных данных"""


def test_correlation_id_uniqueness():
    """Тест что correlation_id уникален для каждого запроса"""
    response1 = client.get("/items/9999")
    response2 = client.get("/items/9998")

    data1 = response1.json()
    data2 = response2.json()

    # Correlation ID должны быть разными
    assert data1["correlation_id"] != data2["correlation_id"]
    # И оба должны быть валидными UUID
    assert len(data1["correlation_id"]) == 36
    assert len(data2["correlation_id"]) == 36
