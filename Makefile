
# ==================================================================================== #
# HELPERS
# ==================================================================================== #

## help: print this help message
.PHONY: help
help:
	@echo 'Usage:'
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^//'

.PHONY: confirm
confirm:
	@echo 'Are you sure? [y/N]' && read ans && [ $${ans:-N} = y ]

# ==================================================================================== #
# DEVELOPMENT
# ==================================================================================== #

## runserver
.PHONY: run
run:
	python3 manage.py runserver 0.0.0.0:8000

## makemigrations
.PHONY: migrations
migrations:
	python3 manage.py makemigrations

## migrate
.PHONY: migrate
migrate:
	python3 manage.py migrate

## tailwind
.PHONY: tailwind
tailwind:
	npm run tailwind-build

## collect
.PHONY: collect
collect:
	python3 manage.py collectstatic

## activate env
.PHONY: env
env:
	source ../myenv/bin/activate