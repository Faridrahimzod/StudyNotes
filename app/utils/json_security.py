import json
from decimal import Decimal
from typing import Any


def safe_json_loads(json_str: str) -> Any:
    """
    Безопасный парсинг JSON с защитой от float-погрешностей
    """
    return json.loads(json_str, parse_float=str)  # Преобразуем float в строку


def safe_json_dumps(obj: Any) -> str:
    """
    Безопасная сериализация JSON с обработкой Decimal
    """

    def decimal_encoder(o):
        if isinstance(o, Decimal):
            return str(o)  # Преобразуем Decimal в строку
        raise TypeError(
            f"Object of type {o.__class__.__name__} is not JSON serializable"
        )

    return json.dumps(obj, default=decimal_encoder, ensure_ascii=False)


def safe_json_response(data: Any) -> dict:
    """
    Подготавливает данные для безопасного возврата в JSON response
    """
    if isinstance(data, (list, dict)):
        json_str = safe_json_dumps(data)
        return json.loads(json_str)  # Возвращаем как native Python объекты
    return data
