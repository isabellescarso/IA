.PHONY: up down app

up:
	docker compose up -d

down:
	docker compose down

app:
	uvicorn src.api.main:app --reload

run: up app