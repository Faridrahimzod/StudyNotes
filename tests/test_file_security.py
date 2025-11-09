from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.utils.file_security import secure_save_file, sniff_content_type

client = TestClient(app)


class TestFileSecurity:
    """Тесты для безопасной работы с файлами"""

    def setup_method(self):
        """Создаем тестовую директорию"""
        self.test_dir = Path("test_uploads")
        self.test_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """Очищаем тестовую директорию"""
        for file in self.test_dir.glob("*"):
            file.unlink()
        self.test_dir.rmdir()

    def test_sniff_content_type_png(self):
        """Тест определения PNG по magic bytes"""
        # Valid PNG signature
        png_data = b"\x89PNG\r\n\x1a\n" + b"fake_png_data"
        assert sniff_content_type(png_data) == "image/png"

    def test_sniff_content_type_jpeg(self):
        """Тест определения JPEG по magic bytes"""
        # Valid JPEG signature
        jpeg_data = b"\xff\xd8" + b"fake_jpeg_data" + b"\xff\xd9"
        assert sniff_content_type(jpeg_data) == "image/jpeg"

    def test_sniff_content_type_unknown(self):
        """Тест определения неизвестного типа"""
        unknown_data = b"invalid_file_data"
        assert sniff_content_type(unknown_data) is None

    def test_secure_save_valid_png(self):
        """Тест безопасного сохранения валидного PNG"""
        png_data = b"\x89PNG\r\n\x1a\n" + b"x" * 1000
        saved_path = secure_save_file(self.test_dir, png_data, "test.png")

        assert saved_path.exists()
        assert saved_path.suffix == ".png"
        # Исправленная проверка - файл должен быть внутри test_dir
        assert saved_path.parent == self.test_dir.resolve()

    def test_secure_save_file_too_large(self):
        """Тест отклонения слишком большого файла"""
        large_data = b"\xff\xd8" + b"x" * (5_000_000 + 1) + b"\xff\xd9"

        with pytest.raises(ValueError, match="File too large"):
            secure_save_file(self.test_dir, large_data, "large.jpg")

    def test_secure_save_unsupported_type(self):
        """Тест отклонения неподдерживаемого типа файла"""
        invalid_data = b"invalid_file_content"

        with pytest.raises(ValueError, match="Unsupported file type"):
            secure_save_file(self.test_dir, invalid_data, "test.txt")

    def test_file_upload_endpoint_success(self):
        """Тест успешной загрузки файла через endpoint"""
        png_data = b"\x89PNG\r\n\x1a\n" + b"fake_png_content"

        response = client.post(
            "/api/v1/files/upload", files={"file": ("test.png", png_data, "image/png")}
        )

        assert response.status_code == 200
        data = response.json()
        assert "saved_as" in data
        assert data["filename"] == "test.png"

    def test_file_upload_too_large(self):
        """Тест отклонения слишком большого файла через endpoint"""
        large_data = b"\xff\xd8" + b"x" * (5_000_000 + 1) + b"\xff\xd9"

        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("large.jpg", large_data, "image/jpeg")},
        )

        assert response.status_code == 413
        assert response.headers["content-type"] == "application/problem+json"

        error_data = response.json()
        assert error_data["type"] == "/errors/file-too-large"
        assert "File exceeds maximum allowed size" in error_data["detail"]

    def test_file_upload_unsupported_type(self):
        """Тест отклонения неподдерживаемого типа через endpoint"""
        invalid_data = b"invalid_content"

        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("test.txt", invalid_data, "text/plain")},
        )

        assert response.status_code == 415
        error_data = response.json()
        assert error_data["type"] == "/errors/unsupported-file-type"
