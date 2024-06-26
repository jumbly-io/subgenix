# Set default shell to bash
SHELL := /bin/bash

# Extract settings from pyproject.toml
NAME := $(shell grep '^name =' pyproject.toml | sed -E "s/name = \"(.*)\"/\\1/")
VERSION := $(shell grep '^version =' pyproject.toml | sed -E "s/version = \"(.*)\"/\\1/")

# Define variables
DOCKER_IMAGE_NAME ?= subgenix
POETRY := poetry
DOCKER := docker
PIP := pip

# Define colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Define styles
BOLD := \033[1m
UNDERLINE := \033[4m

# Define phony targets
.PHONY: build develop install dev-install test format lint image shell ls clean help

# Set default goal to help
.DEFAULT_GOAL := help

## Build the distribution package
build: clean
	@printf "$(BLUE)Building distribution package...$(NC)\n"
	@$(POETRY) build

## Set up the development environment
develop:
	@printf "$(BLUE)Set up the development environment...$(NC)\n"
	@$(POETRY) install
	@$(POETRY) run pre-commit install

## Install the distribution package
install: build
	@printf "$(BLUE)Installing distribution package...$(NC)\n"
	@$(PIP) uninstall -y subgenix  # TODO: Parameterize this.
	@$(PIP) install dist/*.whl

## Run tests
test:
	@printf "$(BLUE)Running tests...$(NC)\n"
	@$(POETRY) run pytest tests

## Format code with black
format:
	@printf "$(BLUE)Formatting code...$(NC)\n"
	@$(POETRY) run black .

## Lint and type-check code with flake8, ruff, mypy
lint:
	@printf "$(BLUE)Linting code...$(NC)\n"
	$(POETRY) run flake8 .
	$(POETRY) run ruff check .
	@printf "$(BLUE)Type-checking code...$(NC)\n"
	@$(POETRY) run mypy src/

## Build Docker image
image:
	@printf "$(BLUE)Building Docker image...$(NC)\n"
	@$(DOCKER) build -t $(DOCKER_IMAGE_NAME) .

## Access a shell Poetry environment
shell:
	@printf "$(BLUE)Accessing Poetry shell...$(NC)\n"
	@$(POETRY) shell

## List all files in the project
ls:
	@printf "$(BLUE)Listing all files in the project...$(NC)\n"
	@git ls-files --cached --others --exclude-standard

## Clean up build artifacts
clean:
	@printf "$(BLUE)Cleaning up build artifacts...$(NC)\n"
	@rm -rf ./dist

## Cycle the installation for interactive testing
iterate: format lint test install
	@printf "$(BLUE)Cycling the installation for interactive testing...$(NC)\n"
	subgenix ~/Videos/393906.mp4 --output ~/Videos/393906.mp4.srt --model medium --use-gpu
	## TODO: Make this portable and parameterize it.

## Display this help message
help:
	@printf "$(BOLD)$(UNDERLINE)Available targets:$(NC)\n\n"
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  $(YELLOW)%-20s$(NC) %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
	@printf "\n$(BOLD)Usage:$(NC)\n"
	@printf "  make $(GREEN)<target>$(NC)\n"
	@printf "\n$(BOLD)Example:$(NC)\n"
	@printf "  make $(GREEN)build$(NC)    $(RED)# Builds the distribution package$(NC)\n"
	@printf "\n$(BOLD)Project:$(NC)\n"
	@printf "  Name: $(GREEN)$(NAME)$(NC)\n"
	@printf "  Version: $(GREEN)$(VERSION)$(NC)\n"
