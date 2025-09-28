from fastapi import APIRouter

router = APIRouter()

@router.get("/tags")
def get_tags():
    """
    Получить все теги (заглушка)
    """
    return {"message": "Tags endpoint - to be implemented"}