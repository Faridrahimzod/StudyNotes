import subprocess

import pytest


class TestContainerSecurity:
    """Тесты безопасности контейнера"""

    def test_container_running_as_non_root(self):
        """Тест что контейнер запущен под non-root пользователем"""
        try:
            result = subprocess.run(
                ["docker", "exec", "secure-app", "id", "-u"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            user_id = result.stdout.strip()
            assert user_id != "0", "Container should not run as root"
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.CalledProcessError,
        ):
            pytest.skip("Container is not running or Docker is not available")

    def test_container_healthcheck(self):
        """Тест что healthcheck проходит успешно"""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "inspect",
                    "secure-app",
                    "--format",
                    "{{.State.Health.Status}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            health_status = result.stdout.strip()
            assert (
                health_status == "healthy"
            ), f"Container should be healthy, got: {health_status}"
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.CalledProcessError,
        ):
            pytest.skip("Container is not running or Docker is not available")

    def test_app_health_endpoint(self):
        """Тест что health endpoint приложения работает"""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "secure-app",
                    "python",
                    "-c",
                    "import requests; requests.get('http://localhost:8000/health', timeout=5)",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert result.returncode == 0, "Health endpoint should return success"
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.CalledProcessError,
        ):
            pytest.skip("Container is not running or Docker is not available")
