
install-libusb:
    sudo apt install libusb-1.0-0

install-dependencies:
    poetry install --no-root
    npm ci

build:
    poetry run make --directory sphinx html
    npm run build

run:
    poetry run gunicorn

run-flask:
    poetry run flask -e .env run
