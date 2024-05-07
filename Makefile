COMPOSE_BASE := docker-compose
LOG_FILE := build.log

build-up:
	$(COMPOSE_BASE)	-f docker-compose.yaml up --build --remove-orphans;

up:	
	$(COMPOSE_BASE)	-f docker-compose.yaml up;

restart:	
	$(COMPOSE_BASE)	-f docker-compose.yaml restart;

down:
	$(COMPOSE_BASE)	-f docker-compose.yaml down;
