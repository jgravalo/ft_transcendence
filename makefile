all:
	docker compose -f docker-compose.yml up -d --build

front:
	docker build -t front ./front
	docker run -d -p 8080:80 front

back:
	docker build -t front ./back
	docker run -d -p 8080:80 back

migrations:
	docker exec -it back python manage.py makemigrations
	docker exec -it back python manage.py migrate

down:
	docker compose -f docker-compose.yml down

ls:
	@docker ps -a
	@echo
	@docker images -a
	@echo
	@docker volume ls 
	@echo
	@docker network ls 

clean:
	@if [ ! -z "$$(docker ps -aq)" ]; then \
		docker stop $$(docker ps -aq); \
		docker rm $$(docker ps -aq); \
	fi
	@if [ ! -z "$$(docker images -aq)" ]; then \
		docker rmi $$(docker images -aq); \
	fi
	@if [ ! -z "$$(docker volume ls -q)" ]; then \
		docker volume rm $$(docker volume ls -q); \
	fi
	@if [ ! -z "$$(docker network ls -q --filter type=custom)" ]; then \
		docker network rm $$(docker network ls -q --filter type=custom); \
	fi

re:
	make clean
	make all

.PHONY: all front back migrations down ls clean