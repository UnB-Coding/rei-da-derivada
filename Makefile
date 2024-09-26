#Configuration

config: copy-env setup-env config-mock entrypoint-chmod
copy-env:
	cp ./api/.env.example ./api/.env
setup-env:
	bash scripts/env.sh
config-mock:
	bash scripts/config.sh
entrypoint-chmod:
	chmod +x ./api/config/entrypoint.sh

# Install dependencies

install:
	pip install -r ./api/requirements.txt
	npm install --prefix ./web

## Docker ##

start-s:
	sudo docker compose up

start:
	sudo docker compose up -d

start-b:
	sudo docker compose up --build -d

stop:
	sudo docker compose down

stop-v:
	sudo docker compose down -v
## Django Shortcuts ##

# Tests
test:
	python3 scripts/test.py --clean

testfull:
	python3 scripts/test.py
	sudo docker exec api-django coverage html
	python3 scripts/report.py
cleanup:
	sudo rm -f api/.coverage
	sudo rm -f -r api/htmlcov
# Migrations
makemigrations:
	sudo docker exec api-django python3 manage.py makemigrations

migrate:
	sudo docker exec api-django python3 manage.py migrate

back:
	docker compose up backend db

front:
	docker compose up frontend
