# Notification Service (Docker-only)

Короткий гайд по запуску сервиса уведомлений (Email, SMS, Telegram) на Django 5.2 + DRF + Celery + Redis + Postgres.

## Требования
- Docker Desktop / Docker Engine + docker compose
- Локальный Python не нужен (всё в контейнерах)

## Быстрый старт
```bash
# 1) Подготовить окружение и собрать образы
make env
make build

# 2) Поднять зависимости и веб
make up-deps
make up
# или одним шагом всё сразу (deps + web + worker + beat)
# make up-all

# 3) Применить миграции и создать админа
make initdb ADMIN_USERNAME=admin ADMIN_PASSWORD=admin ADMIN_EMAIL=admin@example.com

# 4) (опционально) поднять воркеры Celery
make workers-up
```

## Полезные адреса
- Web-приложение: http://localhost:8000
- Django Admin: http://localhost:8000/admin
- MailHog (почта dev): http://localhost:8025

## Эндпоинты API (MVP)
- POST `/api/notifications/send`
- GET `/api/notifications/{id}`

Пример запроса:
```bash
curl -X POST http://localhost:8000/api/notifications/send \
  -H 'Content-Type: application/json' \
  -d '{
    "userId": 123,
    "templateId": "welcome_email",
    "payload": {"name": "Alex"},
    "channelsOrder": ["telegram","email","sms"],
    "idempotencyKey": "user123_welcome_2025-11-20"
  }'
```

## Smoke-тест (автоматически)
```bash
make smoke
```
Тест отправит уведомление, дождётся статуса `sent` или завершит с ошибкой.

## Полезные команды
```bash
make ps         # статус контейнеров
make logs       # логи web (follow)
make stop       # стоп без удаления
make down       # стоп и удаление
make clean      # стоп и удаление + volume'ы
```

## Что ещё не реализовано (заглушки)
- Адаптеры провайдеров: Email (SendGrid/SES), SMS (Twilio), Telegram Bot API
- Вебхуки провайдеров и продвинутые статусы доставки
- UI-дашборд (сейчас минимальный шаблон)
