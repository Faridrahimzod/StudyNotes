from app.database.database import SessionLocal
from app.models.note import Note, User

def seed_data():
    db = SessionLocal()
    
    try:
        # Создаем тестового пользователя
        user = User(
            username="testuser",
            email="test@example.com", 
            hashed_password="hashed_password_123"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Создаем тестовые заметки
        notes = [
            Note(title="Первая заметка", body="Содержание первой заметки", user_id=user.id),
            Note(title="Вторая заметка", body="Содержание второй заметки", user_id=user.id),
            Note(title="Третья заметка", body="Содержание третьей заметки", user_id=user.id),
        ]
        
        for note in notes:
            db.add(note)
        
        db.commit()
        print("Тестовые данные созданы успешно!")
        
    except Exception as e:
        print(f"Ошибка при создании тестовых данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()