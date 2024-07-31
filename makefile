all:
	docker-compose -f ./docker-compose.yml up -d --build

down:
	docker-compose -f ./docker-compose.yml down

ls:
	@echo containers:
	@docker ps -a
	@echo
	@echo images:
	@docker images -a
	@echo
	@echo networks:
	@docker network ls 

clean:
	@docker stop $$(docker ps -qa) #??
	@echo -------- CONTAINERS STOPPED --------
	@docker rm $$(docker ps -qa) #borra contenedor
	@echo -------- CONTAINERS DELETED --------
	@docker rmi -f $$(docker images -qa) #borra imagen
	@echo -------- IMAGES DELETED --------
	@docker network rm jgravalo-pongnet #borra red
	@echo -------- NETWORKS DELETED --------
	@#docker network rm $$(docker network ls -q | grep -v "bridge" | grep -v "host" | grep -v "none")

re:
	make clean
	make all

.PHONY: all down ls clean