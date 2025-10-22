# ADR-003: Rate Limiting for Authentication Endpoints

Дата: 2024-09-28
Статус: Accepted

## Context
Study Notes API подвержен атакам brute-force на endpoints аутентификации. Без ограничения запросов злоумышленники могут:
- Подбирать пароли методом перебора
- Вызывать отказ в обслуживании (DoS)
- Исчерпывать ресурсы сервера

Требуется защитить критические endpoints от злоупотреблений.

## Decision
Внедрить систему ограничения запросов (rate limiting) для следующих endpoints:

1. **Логин endpoint**: 5 попыток в минуту с одного IP
2. **Регистрация**: 3 запроса в минуту с одного IP
3. **Восстановление пароля**: 2 запроса в час с одного IP

Техническая реализация:
- **In-memory хранилище** (Redis) для отслеживания запросов
- **Скользящее окно** (sliding window) алгоритм
- **HTTP заголовки** для информирования клиентов:
  - `X-RateLimit-Limit`: лимит запросов
  - `X-RateLimit-Remaining`: оставшиеся запросы
  - `X-RateLimit-Reset`: время сброса лимита

## Consequences
### Положительные
- Защита от brute-force атак
- Предотвращение DoS атак
- Улучшение стабильности системы
- Соответствие security best practices

### Отрицательные
- Дополнительная сложность инфраструктуры (Redis)
- Возможные false-positive для легитимных пользователей
- Увеличение задержки для проверки лимитов

## Security Impact
- **Снижает риски**: R2 (подбор паролей brute-force), R6 (отказ в обслуживании)
- **Реализует NFR**: NFR-03 (защита от brute-force)
- **Защищает от угроз**: STRIDE - D (Denial of Service)

## Links
- NFR-03 (Защита от brute-force)
- STRIDE: F1 - Denial of Service
- Risks: R2, R6
- Tests: `tests/test_rate_limiting.py`
- Implementation: `app/middleware/rate_limiter.py`
