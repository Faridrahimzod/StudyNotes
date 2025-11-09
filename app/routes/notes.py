from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteResponse
from app.utils.json_security import safe_json_response

router = APIRouter()


@router.get("/notes", response_model=List[NoteResponse])
def get_notes(db: Session = Depends(get_db)):
    """
    Получить все заметки
    """
    notes = db.query(Note).all()
    return notes


@router.get("/")
async def search_notes(
    search: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Поиск заметок с безопасной параметризацией"""
    try:
        query = db.query(Note)

        if search:
            # Безопасный поиск через параметризацию
            query = query.filter(
                Note.title.contains(search) | Note.content.contains(search)
            )

        notes = query.offset(skip).limit(limit).all()

        # Возвращаем безопасно сериализованные данные
        notes_data = []
        for note in notes:
            notes_data.append(
                {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content,
                    "created_at": (
                        note.created_at.isoformat() if note.created_at else None
                    ),
                }
            )

        return safe_json_response(notes_data)

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """
    Получить заметку по ID
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return safe_json_response(
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.isoformat() if note.created_at else None,
        }
    )


@router.post("/notes", response_model=NoteResponse)
def create_note(note_data: NoteCreate, db: Session = Depends(get_db)):
    """
    Создать новую заметку
    """
    # В реальном приложении здесь будет auth и user_id из токена
    user_id = 1  # временно используем тестового пользователя

    # Создаем новую заметку
    new_note = Note(title=note_data.title, body=note_data.body, user_id=user_id)

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note_data: NoteCreate, db: Session = Depends(get_db)):
    """
    Обновить заметку
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Обновляем поля
    note.title = note_data.title
    note.body = note_data.body

    db.commit()
    db.refresh(note)

    return note


@router.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """
    Удалить заметку
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()

    return {"message": "Note deleted successfully"}
