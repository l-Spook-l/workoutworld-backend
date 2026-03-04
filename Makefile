up:
	docker compose up -d

up_rebuild:
	docker compose up --build -d

down:
	docker compose down --remove-orphans

up_rebuild_dev:
	docker compose -f docker-compose-dev.yml up --build -d

up_server:
	docker-compose -f docker-compose-dev.yml up --build -d server_app