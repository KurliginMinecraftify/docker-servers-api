run:
	set -o allexport && source .env && poetry run python -m src

lint:
	poetry run flake8 src/

format:
	poetry run black src/

isort:
	poetry run isort src/

typecheck:
	poetry run mypy src/

build:
	docker-compose build --pull

up:
	docker-compose up --detach

stop:
	docker-compose down