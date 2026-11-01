.PHONY: api web sync up down logs build ps restart

# --- Local (no Docker) ---

api:
	cd apps/api && .venv/bin/uvicorn app.main:app --reload --port 8001

web:
	cd apps/web && npm run dev -- --port 3000

sync:
	curl -s -X POST 'http://127.0.0.1:8001/api/jobs/sync?query=software%20engineer'

# --- Docker (API + Postgres) ---
# App: http://localhost:8000  ·  Learning list: http://localhost:8000/learning-list

up: build
	docker compose up -d
	@echo ""
	@echo "Jobify is starting → http://localhost:8000"
	@echo "Learning list     → http://localhost:8000/learning-list"
	@echo "API health        → http://localhost:8000/api/health"
	@echo "Logs: make logs"

build:
	docker compose build

down:
	docker compose down

restart:
	docker compose restart api

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps
