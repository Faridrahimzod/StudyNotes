from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.note import Note
from app.schemas.note import NoteResponse, NoteCreate

router = APIRouter()

@router.get("/notes", response_model=List[NoteResponse])
def get_notes(db: Session = Depends(get_db)):
    """
    Получить все заметки
    """
    notes = db.query(Note).all()
    return notes

@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """
    Получить заметку по ID
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.post("/notes", response_model=NoteResponse)
def create_note(note_data: NoteCreate, db: Session = Depends(get_db)):
    """
    Создать новую заметку
    """
    # В реальном приложении здесь будет auth и user_id из токена
    user_id = 1  # временно используем тестового пользователя
    
    # Создаем новую заметку
    new_note = Note(
        title=note_data.title,
        body=note_data.body,
        user_id=user_id
    )
    
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