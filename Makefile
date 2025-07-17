# Makefile for the General Assistant project

.PHONY: help setup-venv sync-venv update-venv run-assistant run-webui download-dataset run-docker-compose stop-docker-compose

# Set default goal to 'help'
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make setup-venv            - Set up the development environment (install dependencies and pre-commit hooks)"
	@echo "  make sync-venv             - Sync the development environment"
	@echo "  make update-venv           - Update the development environment"
	@echo "  make download-dataset      - Download the dataset"
	@echo "  make run-assistant         - Run the assistant API server"
	@echo "  make run-webui             - Run the assistant Web UI server"
	@echo "  make run-langgraph-studio  - Run the LangGraph Studio server"
	@echo "  make run-docker-compose    - Run the Docker Compose services"
	@echo "  make stop-docker-compose   - Stop the Docker Compose services"

setup-venv:
	@echo "Setting up development environment..."
	uv sync --all-extras
	uv run pre-commit install
	uv run pre-commit autoupdate
	@echo "Setup complete. Run 'make sync-venv' after git pulls."

sync-venv:
	@echo "Syncing development environment..."
	uv sync --all-extras --frozen
	@echo "Sync complete."	

update-venv:
	@echo "Updating development environment..."
	uv lock --upgrade
	uv sync --all-extras
	@echo "Update complete."

download-dataset:
	@echo "Downloading the dataset..."
	uv run python scripts/download_gaia_dataset.py

run-assistant:
	@echo "Starting the assistant API server..."
	uv run fastapi dev src/general_assistant/api/app.py

run-webui:
	@echo "Starting the assistant Web UI server..."
	uv run chainlit run src/webui/chainlit_main.py -h --no-cache --port 8080 -w

run-langgraph-studio:
	@echo "Starting the LangGraph Studio server..."
	uv run langgraph dev --config scripts/langgraph_studio.json --port 5677 --debug-port 5678

run-docker-compose:
	@echo "Starting the Docker Compose services..."
	docker compose --env-file .env -f deployment/docker/docker-compose.yaml -p general-assistant up --build -d

stop-docker-compose:
	@echo "Stopping the Docker Compose services..."
	docker compose -p general-assistant down