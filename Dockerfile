FROM ghcr.io/prefix-dev/pixi:latest

WORKDIR /app
COPY . /app

RUN pixi install

# To make this work on dokku, you need to:
# 1. `ssh dokku storage:ensure-directory todoapprd`
# 2. `ssh dokku storage:mount todoapprd /var/lib/dokku/data/storage/todoapprd:/app/storage`
#
# Alternatively:
# 1. `ssh <your_user>@<host> "mkdir todoapprd_mount"`
# 2. Create your secret files etc. in `todoapprd_mount` folder
# 3. `ssh dokku storage:mount todoapprd /home/<your_user>/todoapprd_mount:/app/storage`
#
# One can set environment variables with dokku using `dokku config:set`, but for simplicity,
# it is done here. You may also set this variable in /app/storage/.env file. See config.py for more info.

# This is the path to the sqlite database file. It is mounted to /app/storage in the Docker container.
# It is located at /var/lib/dokku/data/storage/todoapprd on the filesystem of the host machine.
# This setup ensures data persistence in the database even if the container is destroyed.
# You could have scp'd .env.prod to the server as /var/lib/dokku/data/storage/todoapprd/.env
# and set the DATABASE_FILE env var there in the file instead.

ENV DATABASE_FILE=serverdatabase.db
ENV ENV=prod

CMD ["sh", "-c", "pixi run populate && pixi run server"]
