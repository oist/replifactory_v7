#git clone http://github.com/catalin-rusnac/replifactory_v7; cd replifactory_v7; make install

default: build-all serve-flask

UI_SERVICE_NAME = ReplifactoryUI
POETRY_VERSION = 1.6.1
PYTHON = poetry run python

.PHONY: build-all build-docs build-vue build

build-all: build-docs build-vue

build-docs:
	cd sphinx && make html

build-vue:
	npm run build

serve-flask:
	$(PYTHON) -m gunicorn -k gevent -w 1 flask_app.app

node_modules: package-lock.json
	npm ci

python_env: poetry.lock
	poetry install

dependencies: node_modules python_env

ifeq ($(OS),Windows_NT)
install: install_win_dependencies dependencies
run: windows-service-compile run-flask
else
install: \
	poetry \
	check_env_variables \
	install_apt_dependencies \
	node-pi \
	updatepath \
	pip \
	ngrok \
	dwservice_install \
	wifi_config \
	dependencies services-ctl
run: run-flask
endif

windows-service-compile: kill-flask build
	cd flask_app && poetry run pyinstaller --noconfirm win32_service.spec

run-flask:
ifeq ($(OS),Windows_NT)
	powershell.exe Start-Process -FilePath "flask_app/dist/win32_service/win32_service.exe" -Verb RunAs -ArgumentList "--startup=auto", "install"
	powershell.exe Start-Process -FilePath "flask_app/dist/win32_service/win32_service.exe" -Verb RunAs start
else
	$(PYTHON) -m gunicorn -k gevent -w 1 flask_app.app
endif

run-vue:
	npm run serve

build:
	npm run build

ngrok:
	@echo "Checking for ngrok..."
	@if ! command -v ngrok > /dev/null; then \
		echo "Installing ngrok..."; \
		curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null; \
		echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list; \
		sudo apt-get update; \
		sudo apt install ngrok; \
		echo "ngrok installed."; \
	else \
		echo "ngrok already installed. No changes made."; \
	fi

swap:
	@if ! grep -q 'CONF_SWAPSIZE=1024' /etc/dphys-swapfile; then \
		echo "Increasing swap size..."; \
		sudo dphys-swapfile swapoff; \
		sudo sed -i 's/CONF_SWAPSIZE=[0-9]*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile; \
		sudo dphys-swapfile setup; \
		sudo dphys-swapfile swapon; \
		echo "Reboot required to increase swap. Please reboot your Raspberry Pi."; \
	else \
		echo "Swap size already 1024. No changes made."; \
	fi

node-pi:
	@if ! command -v node > /dev/null; then \
		echo "Installing Node.js and npm for Raspberry Pi..."; \
		curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -; \
		sudo apt-get install -y nodejs; \
		echo "Node.js and npm installed successfully"; \
	else \
		echo "Node.js and npm already installed. No changes made."; \
	fi

pip:
	@echo "Checking for pip..."
	@if ! command -v pip > /dev/null; then \
  		echo "Installing distutils..."; \
	    sudo apt-get install python3-distutils -y; \
		echo "Installing pip..."; \
		curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; \
		sudo python3 get-pip.py; \
		rm get-pip.py; \
	fi

poetry:
	@echo "Checking for poetry..."
	@if ! command -v poetry > /dev/null; then \
		echo "Installing poetry..."; \
  		curl -sSL https://install.python-poetry.org | POETRY_VERSION=$(POETRY_VERSION) python3 - ; \
	fi

pip-freeze:
	pip freeze -r ./flask_app/requirements.txt > ./flask_app/requirements-lock.txt

copy_to_www:
	@echo "Copying contents of vue/dist/ to /var/www/html..."
	@sudo cp -r vue/dist/* /var/www/html
	@echo "Copied contents of vue/dist/ to /var/www/html."

APT_DEPENDENCIES = \
	python3-distutils \
	python3-scipy \
	python3-numpy \
	python3-pandas \
	libatlas-base-dev \
	python3-dev \
	gfortran \
	libopenblas-dev \
	autossh

install_apt_dependencies: swap
	@echo "Checking for apt dependencies..."
	@sudo apt-get update --allow-releaseinfo-change
	@for dep in $(APT_DEPENDENCIES); do \
		if ! dpkg -s $$dep > /dev/null 2>&1; then \
			sudo apt-get install -y $$dep; \
		fi \
	done

install_win_dependencies:
	cmd /c "(help npm > nul || exit 0) && where npm > nul 2> nul" || winget install -e --id OpenJS.NodeJS.LTS
	cmd /c "(help python > nul || exit 0) && where python > nul 2> nul" || winget install -e --name Python 3.10
	cmd /c "(help qckwinsvc > nul || exit 0) && where qckwinsvc > nul 2> nul" || npm install -g qckwinsvc
	SET POETRY_VERSION=$(POETRY_VERSION) && cmd /c "(help poetry > nul || exit 0) && where poetry > nul 2> nul" \
		|| "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content" | python -

updatepath:
	@if echo $$PATH | grep -q "/home/pi/.local/bin"; then \
		echo "PATH already contains /home/pi/.local/bin. No changes made."; \
	else \
		echo "export PATH=\$$PATH:/home/pi/.local/bin" >> ~/.bashrc; \
		. ~/.bashrc; \
	fi

kill: kill-flask
kill-flask:
ifeq ($(OS),Windows_NT)
	-powershell.exe Start-Process -FilePath "flask_app/dist/win32_service/win32_service.exe" -Verb RunAs stop
	-powershell.exe Start-Process -FilePath "flask_app/dist/win32_service/win32_service.exe" -Verb RunAs uninstall
else
	sudo nohup fuser -k 5000/tcp &
endif

directories:
	@chmod 777 ./
	@if [ ! -d "logs" ]; then \
		echo "Creating logs directory..."; \
		mkdir logs; \
		chmod 777 logs; \
	fi
	@if [ ! -d "db" ]; then \
		echo "Creating db directory..."; \
		mkdir db; \
		chmod 777 db; \
	fi

services-ctl: directories
	@echo "Checking for flask and vue services..."
	@if ! cmp services/flask/flask.service /etc/systemd/system/flask.service >/dev/null 2>&1; then \
		sudo cp services/flask/flask.service /etc/systemd/system/flask.service; \
		echo "Copied services/flask/flask.service to /etc/systemd/system/flask.service"; \
	fi
	@echo "Reloading systemctl daemon..."
	sudo systemctl daemon-reload
	@echo "Enabling flask and vue services..."
	sudo systemctl enable flask.service
	@echo "Starting flask and vue services..."
	sudo systemctl start flask.service

update:
	git pull
	make install
	make kill

push:
	git add .
	git commit -m "update"
	git push

dwservice_install:
	cd services && wget https://www.dwservice.net/download/dwagent.sh
	chmod +x ./services/dwagent.sh

dwservice_run:
	sudo ./services/dwagent.sh -silent key=$(DWSERVICE_KEY)

wifi_config:
	sudo cp services/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf
	sudo chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
	sudo systemctl restart dhcpcd

vps:
	if systemctl is-active --quiet autossh.service; then \
		sudo systemctl stop autossh.service; \
	fi
	sudo cp services/autossh.service /etc/systemd/system/autossh.service
	sudo systemctl daemon-reload
	sudo systemctl enable autossh.service
	sudo systemctl restart autossh.service

check_env_variables:
	@echo "Setting up " $(RASPBERRY_NAME)": "$(VPS_IP)":"$(VPS_PORT)"..."

update-hostname:
	@echo "Setting hostname to $(RASPBERRY_NAME)"
	@echo "$(RASPBERRY_NAME)" | sudo tee /etc/hostname
	@sudo sed -i "s/127.0.1.1.*/127.0.1.1       $(RASPBERRY_NAME)/" /etc/hosts
	@echo "Hostname updated. You may need to reboot for changes to take effect."

secrets:
	make dwservice_run
	make update-hostname
	sudo systemctl daemon-reload
	ssh-keygen -t rsa -b 4096 -C "pi@$(RASPBERRY_NAME)" -f ~/.ssh/id_rsa -N ""
	ssh-copy-id -i ~/.ssh/id_rsa.pub replifactory-device@$(VPS_IP)
	make vps


COMPOSE_OPT = --build --force-recreate
DOCKER_BUILD_OPT =
DOCKER_TAG = replifactory:7-latest

docker-build:
	docker build $(DOCKER_BUILD_OPT) -t $(DOCKER_TAG) .

docker-build-raspberry:
	make docker-build DOCKER_BUILD_OPT="--platform linux/arm/v7"

docker-run:
	docker compose up $(COMPOSE_OPT)

docker-run-daemon:
	docker compose up -d $(COMPOSE_OPT)

docker-logs:
	docker compose logs -f

docker-stop:
	docker compose stop

DEVICE_URL = $(shell poetry run ftdi_urls.py | grep -m 1 -o 'ftdi://[^ ]*/2')
eeprom-write-sn:
	@test -z "$(DEVICE_URL)" && echo "There is no connected device" && exit 1 || exit 0
	@test -z "$$SERIAL_NUMBER" && echo "Define SERIAL_NUMBER" && exit 1 || exit 0
	@echo Write serial number: "$$SERIAL_NUMBER" to device: $(DEVICE_URL)
	poetry run ftconf $(DEVICE_URL) -i data.ini -u -s "$$SERIAL_NUMBER" -o -

eeprom-read:
	@test -z "$(DEVICE_URL)" && echo "There is no connected device" && exit 1 || exit 0
	poetry run ftconf $(DEVICE_URL) -o -

I2C_INTERFACE = $(shell poetry run ftdi_urls.py | grep -o 'ftdi://[^ ]*' | tail -n1)
i2c_scan:
	poetry run i2cscan.py $(I2C_INTERFACE)