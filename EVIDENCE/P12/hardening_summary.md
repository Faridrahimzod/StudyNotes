# P12 – Hardening summary

## Dockerfile
- Переведён на базовый образ `python:3.11-slim` (фиксированная версия вместо `latest`).
- Добавлен отдельный непривилегированный пользователь `appuser`, контейнер запускается от него.
- Открыт только необходимый порт 8000.
- Установка зависимостей через `requirements.txt` с `--no-cache-dir`.

## IaC (Kubernetes)
- Добавлен Deployment и Service для сервиса StudyNotes в `iac/`.
- Включён `securityContext` с `runAsNonRoot: true` и `runAsUser: 1000`.
- Ограничены ресурсы контейнера (`requests`/`limits`).
- Настроены `readinessProbe` и `livenessProbe` на `/health`.
- Service имеет тип `ClusterIP` (не торчит наружу напрямую).

## Trivy
- Образ собирается из Dockerfile и сканируется Trivy (отчёт: `EVIDENCE/P12/trivy_report.json`).
- Результаты просмотрены, критичные уязвимости (если есть) запланированы к устранению через обновление базового образа и зависимостей.
