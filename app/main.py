from decimal import Decimal

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.database.database import create_tables

# Импортируем наши обработчики ошибок
from app.errors import (
    ProblemDetailException,
    generic_exception_handler,
    http_exception_handler,
    problem_detail_handler,
    validation_exception_handler,
)
from app.routes import demo, files, notes, tags
from app.schemas.item import ItemCreate

# Создаем таблицы при запуске
create_tables()

app = FastAPI(
    title="SecDev Course App",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
)

# Регистрируем обработчики ошибок
app.add_exception_handler(ProblemDetailException, problem_detail_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Подключаем Study Notes роутеры
app.include_router(notes.router, prefix="/api/v1", tags=["study-notes"])
app.include_router(tags.router, prefix="/api/v1", tags=["study-notes-tags"])
app.include_router(files.router, prefix="/api/v1", tags=["files"])
app.include_router(demo.router, prefix="/api/v1", tags=["demo"])


@app.get("/health")
def health():
    return {"status": "ok"}


# Example minimal entity (for tests/demo)
_DB = {"items": []}


@app.post("/items")
async def create_item(item: ItemCreate):
    # Безопасная сериализация JSON с обработкой Decimal
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return str(obj)  # Преобразуем Decimal в строку безопасно
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    # Возвращаем валидированные и нормализованные данные
    return {
        "id": 1,
        "name": item.name,
        "price": str(item.price) if item.price else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@app.get("/items/{item_id}")
def get_item(item_id: int):
    for it in _DB["items"]:
        if it["id"] == item_id:
            return it
    raise ProblemDetailException(
        status_code=404,
        title="Not Found",
        detail="item not found",
        error_type="/errors/not-found",
    )
