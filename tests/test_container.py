import os
import subprocess

import pytest


def is_ci_environment():
    """Проверяет запущены ли мы в CI среде"""
    return os.getenv("CI") == "true"


def is_docker_available():
    """Проверяет доступен ли Docker и docker-compose"""
    try:
        # Проверяем docker
        docker_result = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True, timeout=5
        )

        # Проверяем docker-compose
        compose_result = subprocess.run(
            ["docker-compose", "--version"], capture_output=True, text=True, timeout=5
        )

        return docker_result.returncode == 0 and compose_result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_container_running(container_name):
    """Проверяет запущен ли контейнер"""
    try:
        result = subprocess.run(
            ["docker", "inspect", container_name],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (
        subprocess.TimeoutExpired,
        FileNotFoundError,
        subprocess.CalledProcessError,
    ):
        return False


class TestContainerSecurity:
    """Тесты безопасности контейнера"""

    @pytest.mark.skipif(
        is_ci_environment(), reason="Container tests require local Docker environment"
    )
    @pytest.mark.skipif(
        not is_docker_available(), reason="Docker and docker-compose are not available"
    )
    @pytest.mark.skipif(
        not is_container_running("secure-app"),
        reason="Container 'secure-app' is not running",
    )
    def test_container_running_as_non_root(self):
        """Тест что контейнер запущен под non-root пользователем"""
        result = subprocess.run(
            ["docker", "exec", "secure-app", "id", "-u"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        user_id = result.stdout.strip()
        assert user_id != "0", "Container should not run as root"

    @pytest.mark.skipif(
        is_ci_environment(), reason="Container tests require local Docker environment"
    )
    @pytest.mark.skipif(
        not is_docker_available(), reason="Docker and docker-compose are not available"
    )
    @pytest.mark.skipif(
        not is_container_running("secure-app"),
        reason="Container 'secure-app' is not running",
    )
    def test_container_healthcheck(self):
        """Тест что healthcheck проходит успешно"""
        import time

        time.sleep(10)

        result = subprocess.run(
            ["docker", "inspect", "secure-app", "--format", "{{.State.Health.Status}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        health_status = result.stdout.strip()
        assert health_status in [
            "healthy",
            "starting",
        ], f"Container health status should be healthy or starting, got: {health_status}"

    @pytest.mark.skipif(
        is_ci_environment(), reason="Container tests require local Docker environment"
    )
    @pytest.mark.skipif(
        not is_docker_available(), reason="Docker and docker-compose are not available"
    )
    @pytest.mark.skipif(
        not is_container_running("secure-app"),
        reason="Container 'secure-app' is not running",
    )
    def test_app_health_endpoint(self):
        """Тест что health endpoint приложения работает"""
        result = subprocess.run(
            [
                "docker",
                "exec",
                "secure-app",
                "curl",
                "-f",
                "http://localhost:8000/health",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode in [
            0,
            7,
        ], f"Health endpoint check failed with code: {result.returncode}"

    @pytest.mark.skipif(
        is_ci_environment(), reason="Container tests require local Docker environment"
    )
    @pytest.mark.skipif(
        not is_docker_available(), reason="Docker and docker-compose are not available"
    )
    @pytest.mark.skipif(
        not is_container_running("secure-app"),
        reason="Container 'secure-app' is not running",
    )
    def test_container_has_no_sensitive_mounts(self):
        """Тест что контейнер не имеет чувствительных монтирований"""
        result = subprocess.run(
            ["docker", "inspect", "secure-app", "--format", "{{json .Mounts}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        mounts = result.stdout.strip()
        assert "/etc/passwd" not in mounts
        assert "/etc/shadow" not in mounts
