all:
	docker compose -f docker-compose.yml up -d --build

down:
	docker compose -f docker-compose.yml down

front:
	docker build -t front ./front
	docker run -d front

back:
	docker build -t back ./back
	docker run -d back

db:
	docker build -t db ./db
	docker run -d -p 5432:5432 db

migrations:
	docker exec -it back python manage.py makemigrations
	docker exec -it back python manage.py migrate

dbshell:
	docker exec -it db psql -U postgres -d postgres


ls:
	@docker ps -a
	@echo
	@docker images -a
	@echo
	@docker volume ls 
	@echo
	@docker network ls 

clean:
	@echo "Deteniendo y eliminando contenedores..."
	@docker compose down
	@if [ ! -z "$$(docker ps -aq)" ]; then \
		docker stop $$(docker ps -aq); \
		docker rm $$(docker ps -aq); \
	fi
	@echo "Eliminando imágenes..."
	@docker rmi -f $$(docker images -aq) 2>/dev/null || true
	@echo "Eliminando volúmenes..."
	@docker volume rm $$(docker volume ls -q) 2>/dev/null || true
	@echo "Eliminando redes personalizadas..."
	@docker network rm $$(docker network ls -q --filter type=custom) 2>/dev/null || true

# Entrar en el contenedor con 'make enter SERVICE=front(o back)
enter:
	@CONTAINER_ID=$$(docker compose -f docker-compose.yml ps -q $(SERVICE)); \
	if [ -n "$$CONTAINER_ID" ]; then \
		docker exec -it $$CONTAINER_ID /bin/sh; \
	else \
		echo "Container for service '$(SERVICE)' is not running"; \
	fi

re:
	make clean
	make all

.PHONY: all down front back migrations dbshell ls clean enter