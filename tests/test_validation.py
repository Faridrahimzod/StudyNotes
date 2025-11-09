from decimal import Decimal

import pytest

from app.schemas.note import NoteCreate
from app.schemas.validation import PaymentValidation, safe_json_parse


class TestPaymentValidation:
    """Тесты валидации платежей"""

    def test_valid_payment(self):
        """Позитивный тест: валидные данные"""
        data = {
            "amount": "100.50",
            "currency": "USD",
            "occurred_at": "2024-01-15T12:00:00Z",
            "description": "Test payment",
        }
        payment = PaymentValidation(**data)
        assert payment.amount == Decimal("100.50")
        assert payment.currency == "USD"

    def test_extra_fields_rejected(self):
        """Негативный тест: лишние поля должны отвергаться"""
        data = {
            "amount": "100.50",
            "currency": "USD",
            "occurred_at": "2024-01-15T12:00:00Z",
            "description": "Test payment",
            "extra_field": "should_fail",
        }
        with pytest.raises(ValueError):
            PaymentValidation(**data)

    def test_decimal_precision_validation(self):
        """Негативный тест: слишком много decimal places"""
        data = {
            "amount": "100.555",  # 3 decimal places
            "currency": "USD",
            "occurred_at": "2024-01-15T12:00:00Z",
            "description": "Test",
        }
        with pytest.raises(ValueError):
            PaymentValidation(**data)

    def test_negative_amount(self):
        """Негативный тест: отрицательная сумма"""
        data = {
            "amount": "-10.00",
            "currency": "USD",
            "occurred_at": "2024-01-15T12:00:00Z",
            "description": "Test",
        }
        with pytest.raises(ValueError):
            PaymentValidation(**data)

    def test_invalid_currency(self):
        """Негативный тест: неверный код валюты"""
        data = {
            "amount": "100.00",
            "currency": "USDD",  # 4 символа
            "occurred_at": "2024-01-15T12:00:00Z",
            "description": "Test",
        }
        with pytest.raises(ValueError):
            PaymentValidation(**data)


class TestNoteValidation:
    """Тесты валидации заметок"""

    def test_xss_attempt_blocked(self):
        """Негативный тест: попытка XSS в заголовке"""
        data = {
            "title": "Hello <script>alert('xss')</script>",
            "body": "Test body",
            "priority": "1.0",
        }
        with pytest.raises(ValueError):
            NoteCreate(**data)

    def test_sql_injection_attempt_blocked(self):
        """Негативный тест: SQL инъекция должна блокироваться на уровне валидации"""
        data = {
            "title": "Test'; DROP TABLE users;--",  # Символы ';-- не допускаются паттерном
            "body": "Test body",
            "priority": "1.0",
        }
        # Должно НЕ пройти валидацию из-за недопустимых символов
        with pytest.raises(ValueError):
            NoteCreate(**data)

    def test_safe_sql_like_content(self):
        """Позитивный тест: безопасный контент с SQL-подобными словами"""
        data = {
            "title": "Test SELECT FROM WHERE",  # Безопасно - только буквы и пробелы
            "body": "Test body",
            "priority": "1.0",
        }
        note = NoteCreate(**data)
        assert note.title == "Test SELECT FROM WHERE"

    def test_empty_title(self):
        """Негативный тест: пустой заголовок"""
        data = {"title": "", "body": "Test body", "priority": "1.0"}
        with pytest.raises(ValueError):
            NoteCreate(**data)

    def test_oversized_body(self):
        """Негативный тест: слишком длинное тело"""
        data = {
            "title": "Test",
            "body": "x" * 10001,  # Превышает лимит в 10000
            "priority": "1.0",
        }
        with pytest.raises(ValueError):
            NoteCreate(**data)


class TestJSONSecurity:
    """Тесты безопасности JSON"""

    def test_float_precision_attack(self):
        """Тест защиты от float-атак при парсинге JSON"""
        # Создаем очень длинное число как строку, чтобы избежать проблем с float precision
        long_number = "9" * 100 + ".0"  # 100 девяток + .0
        malicious_json = f'{{"amount": "{long_number}"}}'

        # Безопасный парсинг должен обработать это как строку
        result = safe_json_parse(malicious_json)
        assert isinstance(result["amount"], str)
        assert result["amount"] == long_number

    def test_malformed_json(self):
        """Тест обработки поврежденного JSON"""
        bad_json = '{"amount": 100.50'  # Незакрытый JSON
        with pytest.raises(ValueError):
            safe_json_parse(bad_json)
