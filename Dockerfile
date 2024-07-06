FROM ghcr.io/prefix-dev/pixi:latest

WORKDIR /app
COPY . /app

RUN pixi install

# to make this work on doccu you need:
# 1. `ssh dokku storage:ensure-directory todoapprd`
# 2. `ssh dokku storage:mount todoapprd /var/lib/dokku/data/storage/todoapprd:/app/storage`
#
# Or you can also do:
# 1. `ssh docker "mkdir todoapprd_mount"`..this runs as your user on the host machine
# 2. Create your screts files etc in `todoapprd_mount` folder
# 3. `ssh dokku storage:mount todoapprd /home/your_user/todoapprd_mount:/app/storage`
# One can set env variables with dokku see "dokku config set" but i do it here for simplicity
# one may also set this variable in /app/storage/.env file. See config.py for more info.

# This is the path to the sqlite database file. It is mounted to /app/storage in the docker container.
# It is at /var/lib/dokku/data/storage/todoapprd on the filesystem of the host machine.
# This is done to persist the data in the database even if the container is destroyed.
# You could have scp'd .env.prod to the server as /var/lib/dokku/data/storage/todoapprd/.env
# and set the DATABASE_FILE env var there in the file instead.

ENV DATABASE_FILE=serverdatabase.db
ENV ENV=prod

CMD pixi run populate; pixi run server
