.PHONY: build up down logs shell migrate superuser static test clean

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

# Django commands
shell:
	docker-compose exec web python manage.py shell

migrate:
	docker-compose exec web python manage.py migrate

migrations:
	docker-compose exec web python manage.py makemigrations

superuser:
	docker-compose exec web python manage.py createsuperuser

static:
	docker-compose exec web python manage.py collectstatic --noinput

test:
	docker-compose exec web python manage.py test

# Database
db-reset:
	docker-compose down -v
	docker-compose up -d db
	sleep 5
	docker-compose exec web python manage.py migrate

# Cleanup
clean:
	docker-compose down -v
	docker system prune -f

# Full setup
setup:
	cp .env.example .env
	docker-compose build
	docker-compose up -d
	sleep 10
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py createsuperuser

# Restart
restart:
	docker-compose restart

# Status
status:
	docker-compose ps
