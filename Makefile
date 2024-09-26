up:
	docker-compose up -d

up_rebuild:
	docker-compose up --build -d

down:
	docker-compose down --remove-orphans
