#Configuration

config: copy-env setup-env config-mock
copy-env:
	cp ./api/.env.example ./api/.env
setup-env:
	bash scripts/env.sh
config-mock:
	bash scripts/config.sh

# Install dependencies

install:
	pip install -r ./api/requirements.txt

## Docker ##

start:
	sudo docker compose up -d

start-b:
	sudo docker compose up --build -d

stop:
	sudo docker compose down

stop-v:
	sudo docker compose down -v
