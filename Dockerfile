FROM ghcr.io/prefix-dev/pixi:latest

WORKDIR /app
COPY . /app

RUN pixi install

ENV DATABASE_FILE=/app/storage/serverdatabase.db
ENV ENV=prod

CMD pixi run populate; pixi run server
