from decimal import Decimal

from fastapi import APIRouter

from app.utils.json_security import safe_json_loads, safe_json_response

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/decimal-test")
async def decimal_demo():
    """Endpoint для демонстрации безопасной работы с Decimal"""
    data = {
        "small_decimal": Decimal("0.1"),
        "large_decimal": Decimal("1234567890.1234567890"),
        "float_number": 0.1 + 0.2,  # Известная проблема с float
        "regular_string": "test",
    }

    return safe_json_response(data)


@router.post("/parse-json")
async def parse_json_demo(json_data: str):
    """Endpoint для демонстрации безопасного парсинга JSON"""
    try:
        parsed_data = safe_json_loads(json_data)
        return {
            "original": json_data,
            "parsed": parsed_data,
            "float_values_converted_to_string": True,
        }
    except Exception as e:
        return safe_json_response({"error": str(e), "message": "Invalid JSON provided"})
