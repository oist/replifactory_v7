#ARG RUST_VERION=1.74.1
# FROM fnndsc/python-poetry:1.5.1 as poetry
FROM python:3.10.13-bullseye as python-base

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.7.1 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" 

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

#FROM rust:${RUST_VERION}-slim as rust

# BUILDER
FROM python-base as builder-base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential


# install Rust needs for cryptography
ENV CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH=/usr/local/cargo/bin:$PATH \
    RUST_VERSION=1.74.1
#COPY --from=rust $CARGO_HOME $CARGO_HOME
#COPY --from=rust $RUSTUP_HOME $RUSTUP_COME
#RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
RUN set -eux; \
    dpkgArch="$(dpkg --print-architecture)"; \
    case "${dpkgArch##*-}" in \
        amd64) rustArch='x86_64-unknown-linux-gnu'; rustupSha256='0b2f6c8f85a3d02fde2efc0ced4657869d73fccfce59defb4e8d29233116e6db' ;; \
        armhf) rustArch='armv7-unknown-linux-gnueabihf'; rustupSha256='f21c44b01678c645d8fbba1e55e4180a01ac5af2d38bcbd14aa665e0d96ed69a' ;; \
        arm64) rustArch='aarch64-unknown-linux-gnu'; rustupSha256='673e336c81c65e6b16dcdede33f4cc9ed0f08bde1dbe7a935f113605292dc800' ;; \
        i386) rustArch='i686-unknown-linux-gnu'; rustupSha256='e7b0f47557c1afcd86939b118cbcf7fb95a5d1d917bdd355157b63ca00fc4333' ;; \
        *) echo >&2 "unsupported architecture: ${dpkgArch}"; exit 1 ;; \
    esac; \
    url="https://static.rust-lang.org/rustup/archive/1.26.0/${rustArch}/rustup-init"; \
    wget "$url"; \
    echo "${rustupSha256} *rustup-init" | sha256sum -c -; \
    chmod +x rustup-init; \
    ./rustup-init -y --no-modify-path --profile minimal --default-toolchain $RUST_VERSION --default-host ${rustArch}; \
    rm rustup-init; \
    chmod -R a+w $RUSTUP_HOME $CARGO_HOME; \
    rustup --version; \
    cargo --version; \
    rustc --version;
#RUN ls -l $CARGO_HOME/bin; echo $PATH; rustc --version
# install poetry - respects $POETRY_VERSION & $POETRY_HOME
# RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
RUN pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - || cat /poetry-installer-error-*.log

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH

COPY --from=project_root poetry.lock poetry.toml pyproject.toml ./

RUN apt-get update \
    && apt-get install --no-install-recommends -y cmake libblas3 libblas-dev \
    && cmake --version

# RUN poetry export -f requirements.txt --output /tmp/requirements.txt
RUN poetry install --only main


# PRODUCTION
FROM python-base as production

RUN apt-get update && apt-get install -y \
    libusb-1.0 \
    && rm -rf /var/lib/apt/lists/*

ARG USER=flask

ENV USER_NAME=$USER

COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR /usr/src/app

RUN useradd -mU $USER_NAME && \
    chown $USER_NAME:$USER_NAME ./ && \
    usermod -aG plugdev $USER

USER $USER

# COPY --from=poetry /tmp/requirements.txt ./requirements-lock.txt

# RUN pip install --no-cache-dir -r requirements-lock.txt

COPY --chown=$USER:$USER . .

RUN chmod +x entrypoint.sh

ENV PATH=$PATH:/home/flask/.local/bin/

ENTRYPOINT ["./entrypoint.sh"]
