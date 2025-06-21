# Makefile para automação do projeto

.PHONY: help install test run clean lint format

help: ## Mostra este menu de ajuda
	@echo "Comandos disponíveis:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instala as dependências
	pip install -r requirements.txt

test: ## Executa todos os testes
	pytest tests/ -v

test-unit: ## Executa apenas testes unitários
	pytest tests/ -v -m "unit"

test-integration: ## Executa apenas testes de integração
	pytest tests/ -v -m "integration"

test-coverage: ## Executa testes com cobertura
	pytest tests/ --cov=app --cov-report=html --cov-report=term

run: ## Inicia o servidor de desenvolvimento
	python wsgi.py

run-prod: ## Inicia o servidor de produção
	gunicorn -c gunicorn_config.py wsgi:app

migrate: ## Executa migrações do banco
	flask db upgrade

migrate-create: ## Cria uma nova migração
	flask db migrate -m "$(MSG)"

clean: ## Limpa arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

lint: ## Verifica qualidade do código
	flake8 app/ tests/

format: ## Formata o código
	black app/ tests/

setup-dev: install migrate ## Configura ambiente de desenvolvimento
	@echo "Ambiente de desenvolvimento configurado!"

docker-build: ## Constrói a imagem Docker
	docker build -t automacao-python .

docker-run: ## Executa o container Docker
	docker-compose up

# Comandos específicos do projeto
api-test: ## Executa teste da API
	python test_asset_api.py

demo: ## Executa demonstração completa
	@echo "Iniciando demonstração..."
	python wsgi.py &
	@sleep 5
	python test_asset_api.py
	@pkill -f "python wsgi.py"
