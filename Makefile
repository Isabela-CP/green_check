# Comando padrão: desenvolvimento
dev:
	docker compose up --build

# Parar os containers
down:
	docker compose down

soft-clean:
	sudo rm -rf ./db/data && docker compose down --remove-orphans

# Limpar tudo (containers, volumes, cache de build)
clean:
	sudo rm -rf ./db/data && docker compose down -v --rmi all --remove-orphans