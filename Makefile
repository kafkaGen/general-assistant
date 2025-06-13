# Makefile for the General Assistant project

.PHONY: help setup run-assistant run-webui

# Set default goal to 'help'
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make setup          - Set up the development environment (install dependencies and pre-commit hooks)"
	@echo "  make run-assistant  - Run the assistant API server"
	@echo "  make run-webui      - Run the assistant Web UI server"

setup-venv:
	@echo "Setting up development environment..."
	uv sync --all-extras
	pre-commit install
	pre-commit autoupdate
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

run-assistant:
	@echo "Starting the assistant API server..."
	fastapi dev src/general_assistant/api/app.py

run-webui:
	@echo "Starting the assistant Web UI server..."
	chainlit run src/general_assistant/api/webui.py