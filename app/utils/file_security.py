import uuid
from pathlib import Path
from typing import Optional

# Константы
MAX_FILE_SIZE = 5_000_000  # 5MB
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"


def sniff_content_type(data: bytes) -> Optional[str]:
    """Определяет MIME-тип по magic bytes"""
    if data.startswith(PNG_SIGNATURE):
        return "image/png"
    if data.startswith(JPEG_SOI) and data.endswith(JPEG_EOI):
        return "image/jpeg"
    return None


def secure_save_file(
    upload_dir: Path, file_data: bytes, original_filename: str
) -> Path:
    """
    Безопасно сохраняет файл с проверками:
    - Magic bytes
    - Лимит размера
    - Канонизация пути
    - UUID имя файла
    - Запрет симлинков
    """
    # Проверка размера файла
    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError("File too large")

    # Проверка magic bytes
    content_type = sniff_content_type(file_data)
    if not content_type:
        raise ValueError("Unsupported file type")

    # Определяем расширение на основе типа контента
    extension = ".png" if content_type == "image/png" else ".jpg"

    # Создаем UUID имя файла
    filename = f"{uuid.uuid4()}{extension}"

    # Канонизация пути
    upload_dir = upload_dir.resolve(strict=True)
    file_path = (upload_dir / filename).resolve()

    # Проверка что файл остается внутри целевой директории
    if not str(file_path).startswith(str(upload_dir)):
        raise ValueError("Path traversal attempt detected")

    # Проверка на симлинки в родительских директориях
    current_path = upload_dir
    while current_path != current_path.parent:  # пока не дошли до корня
        if current_path.is_symlink():
            raise ValueError("Symlinks not allowed in path")
        current_path = current_path.parent

    # Сохраняем файл
    file_path.write_bytes(file_data)
    return file_path


def validate_file_path(root_dir: Path, file_path: Path) -> bool:
    """Проверяет что файл находится внутри корневой директории"""
    try:
        root_dir = root_dir.resolve(strict=True)
        file_path = file_path.resolve(strict=True)
        return str(file_path).startswith(str(root_dir))
    except (FileNotFoundError, RuntimeError):
        return False
