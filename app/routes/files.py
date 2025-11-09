from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from app.errors import ProblemDetailException
from app.utils.file_security import secure_save_file

router = APIRouter(prefix="/files", tags=["files"])

# Создаем директорию для загрузок если не существует
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint для безопасной загрузки файлов
    """
    try:
        # Читаем файл
        file_data = await file.read()

        # Сохраняем файл с безопасными проверками
        saved_path = secure_save_file(UPLOAD_DIR, file_data, file.filename)

        return {
            "filename": file.filename,
            "saved_as": saved_path.name,
            "size": len(file_data),
            "message": "File uploaded securely",
        }

    except ValueError as e:
        error_msg = str(e)
        if "too large" in error_msg:
            raise ProblemDetailException(
                status_code=413,
                title="File Too Large",
                detail="File exceeds maximum allowed size (5MB)",
                error_type="/errors/file-too-large",
            )
        elif "Unsupported file type" in error_msg:
            raise ProblemDetailException(
                status_code=415,
                title="Unsupported Media Type",
                detail="Only PNG and JPEG images are supported",
                error_type="/errors/unsupported-file-type",
            )
        elif "Path traversal" in error_msg or "Symlinks" in error_msg:
            raise ProblemDetailException(
                status_code=400,
                title="Bad Request",
                detail="Invalid file path",
                error_type="/errors/invalid-path",
            )
        else:
            raise ProblemDetailException(
                status_code=400,
                title="Bad Request",
                detail=error_msg,
                error_type="/errors/file-validation",
            )
    except Exception:
        raise ProblemDetailException(
            status_code=500,
            title="Internal Server Error",
            detail="Failed to process file upload",
            error_type="/errors/file-upload-failed",
        )
