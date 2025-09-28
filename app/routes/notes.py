from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.note import Note
from app.schemas.note import NoteResponse

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