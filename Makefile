# Make shortcuts for Docker-only workflow

COMPOSE := docker compose
WEB := web
DEPS := postgres redis mailhog
WORKERS := worker beat

# admin defaults (override with: make superuser ADMIN_USERNAME=foo ADMIN_PASSWORD=bar)
ADMIN_USERNAME ?= admin
ADMIN_EMAIL ?= admin@example.com
ADMIN_PASSWORD ?= admin

.PHONY: help env build up up-deps up-all workers-up down stop ps logs makemigrations migrate initdb superuser restart smoke clean

help:
	@echo "Available targets:"
	@echo "  env            - create .env from .env.example if missing"
	@echo "  build          - build images"
	@echo "  up-deps        - start deps (postgres, redis, mailhog)"
	@echo "  up             - start web"
	@echo "  up-all         - start deps + web + workers (worker, beat)"
	@echo "  workers-up     - start workers (worker, beat)"
	@echo "  makemigrations - run Django makemigrations"
	@echo "  migrate        - run Django migrate"
	@echo "  superuser      - create Django superuser (use ADMIN_* vars)"
	@echo "  initdb         - makemigrations + migrate + superuser"
	@echo "  ps             - show compose ps"
	@echo "  logs           - tail web logs"
	@echo "  restart        - restart web"
	@echo "  smoke          - run smoke test (POST send, poll status)"
	@echo "  stop           - stop all services"
	@echo "  down           - stop and remove services"
	@echo "  clean          - down with volumes"

env:
	@test -f .env || cp .env.example .env

build:
	$(COMPOSE) build

up-deps:
	$(COMPOSE) up -d $(DEPS)

up:
	$(COMPOSE) up -d $(WEB)

up-all: up-deps
	$(COMPOSE) up -d $(WEB) $(WORKERS)

workers-up:
	$(COMPOSE) up -d $(WORKERS)

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f $(WEB)

restart:
	$(COMPOSE) restart $(WEB)

makemigrations:
	$(COMPOSE) run --rm $(WEB) bash -lc "python app/manage.py makemigrations"

migrate:
	$(COMPOSE) run --rm $(WEB) bash -lc "python app/manage.py migrate"

superuser:
	$(COMPOSE) run --rm \
	  -e DJANGO_SUPERUSER_USERNAME=$(ADMIN_USERNAME) \
	  -e DJANGO_SUPERUSER_EMAIL=$(ADMIN_EMAIL) \
	  -e DJANGO_SUPERUSER_PASSWORD=$(ADMIN_PASSWORD) \
	  $(WEB) bash -lc "python app/manage.py createsuperuser --noinput || true"

initdb: makemigrations migrate superuser

stop:
	$(COMPOSE) stop

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v

smoke: up-all
	# send notification and poll status until 'sent' or timeout
	$(COMPOSE) run --rm $(WEB) bash -lc 'set -e; \
	  RES=$$(curl -s -X POST http://web:8000/api/notifications/send -H "Content-Type: application/json" \
	    -d '\''{"userId":1,"templateId":"welcome_email","payload":{"name":"Smoke"},"channelsOrder":["telegram","email","sms"]}'\'' ); \
	  echo "POST response: $$RES"; \
	  ID=$$(python -c '\''import sys, json; print(json.load(sys.stdin)["notificationId"])'\'' <<<"$$RES"); \
	  echo "Notification ID: $$ID"; \
	  for i in $$(seq 1 20); do \
	    STATUS=$$(curl -s http://web:8000/api/notifications/$$ID | python -c '\''import sys, json; print(json.load(sys.stdin).get("status", ""))'\''); \
	    echo "Attempt $$i: status=$$STATUS"; \
	    [ "$$STATUS" = "sent" ] && break; \
	    sleep 1; \
	  done; \
	  [ "$$STATUS" = "sent" ] || (echo "SMOKE FAILED" && exit 1); \
	  echo "SMOKE OK"'
