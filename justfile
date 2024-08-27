
install-libusb:
    sudo apt install libusb-1.0-0

install-dependencies: install-python-dependencies install-npm-dependencies

install-python-dependencies:
    poetry install --no-root

install-npm-dependencies:
    npm ci

install: build
    poetry install

build: changelog build-docs build-vue build-app

build-docs: install-python-dependencies
    poetry run make --directory documentation html

build-vue: install-npm-dependencies
    npm run build

build-app: install-python-dependencies
    poetry build

pre-commit-install:
    poetry run pre-commit install

pre-commit-run:
    poetry run pre-commit run --all-files

lint: lint-app lint-vue

lint-app:
    poetry run black --check backend backend_tests

lint-vue:


run: install
    poetry run replifactory

run-flask:
    poetry run flask -e .env run

run-vue:
    npm run serve

test:
    poetry run pytest

changelog:
    poetry run git-changelog

bump-version:
    poetry run git-changelog --bump auto
