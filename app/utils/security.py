import json


def safe_json_parse(json_str: str):
    """Безопасный парсинг JSON с обработкой float как строк"""
    return json.loads(json_str, parse_float=str)  # Избегаем проблем с float
