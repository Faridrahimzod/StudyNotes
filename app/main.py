from fastapi import FastAPI, HTTPException

from app.database.database import create_tables

# Импортируем наши обработчики ошибок
from app.errors import (
    ProblemDetailException,
    generic_exception_handler,
    http_exception_handler,
    problem_detail_handler,
)
from app.routes import notes, tags

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

# Подключаем Study Notes роутеры
app.include_router(notes.router, prefix="/api/v1", tags=["study-notes"])
app.include_router(tags.router, prefix="/api/v1", tags=["study-notes-tags"])


@app.get("/health")
def health():
    return {"status": "ok"}


# Example minimal entity (for tests/demo)
_DB = {"items": []}


@app.post("/items")
def create_item(name: str):
    if not name or len(name) > 100:
        raise ProblemDetailException(
            status_code=422,
            title="Validation Error",
            detail="name must be 1..100 chars",
            error_type="/errors/validation",
        )
    item = {"id": len(_DB["items"]) + 1, "name": name}
    _DB["items"].append(item)
    return item


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
