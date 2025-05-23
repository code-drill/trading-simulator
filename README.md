## Source

https://github.com/code-drill/django-app-template

## Development

### Build image to use it as python interpreter image name: `trading-simulator:dev`

```shell
./app_build.bsh
# or app_build.cmd
```

### Run shell inside container

```shell
./app_shell.bsh
# or app_shell.cmd
/app/app/bin/init-dev.bsh
```

### Start app

```shell
./app_start.bsh
# or app_start.cmd
```

## Usage

```shell
# Build container
## linux / wsl2
docker compose build --build-arg userid=$(id -u) --build-arg groupid=$(id -g)
# or
./app_build.bsh
## windows
docker compose build
# or
app_build.cmd

# Enter container
docker compose run --remove-orphans  -P django /bin/bash
docker compose run -P django /bin/bash
./app_shell.bsh
app_build.cmd

# Install Django and other dependencies
./app_shell.bsh # or app_build.cmd
uv sync

# running django commands
## enter container
./app_shell.bsh # or app_build.cmd
## switch dir to django source
cd app/src
# and than run command
uv run manage.py makemigrations
uv run manage.py collectstatic
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver 0.0.0.0:8000

# Run the fullstack
uv run honcho start
# or
./app_start.cmd
# or
./app_start.bsh
```

## Structure

- project venv is located under: /home/app_user/venv/bin/
- project interpretator is located under: /home/app_user/venv/bin/python

## How to

### Add App

```shell
./app_shell.bsh # or app_shell.cmd
cd app/src
uv run manage.py startapp NEW_APP_NAME
```

### Pycharm setup

- you can use `PROJECT_SLUG:dev` docker image as a interpretator. it is build always when running
  app_build.cmd/app_build.bsh

### dev bas setup - migrate, create superuser, collect static

- you can use `/app/app/bin/init-dev.bsh` script to perform all of these three task

