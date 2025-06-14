# Makefile for the General Assistant project

.PHONY: help setup-venv sync-venv update-venv run-assistant run-webui download-dataset

# Set default goal to 'help'
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make setup-venv          - Set up the development environment (install dependencies and pre-commit hooks)"
	@echo "  make sync-venv           - Sync the development environment"
	@echo "  make update-venv         - Update the development environment"
	@echo "  make run-assistant       - Run the assistant API server"
	@echo "  make run-webui           - Run the assistant Web UI server"
	@echo "  make download-dataset    - Download the dataset"

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
	uv run fastapi dev src/general_assistant/api/app.py

run-webui:
	@echo "Starting the assistant Web UI server..."
	uv run chainlit run src/webui/chainlit_main.py -h --no-cache --port 8080

download-dataset:
	@echo "Downloading the dataset..."
	uv run python scripts/download_gaia_dataset.py
