FROM ghcr.io/prefix-dev/pixi:latest

WORKDIR /app
COPY . /app

# Install dependencies using pixi
RUN pixi install

# Install gunicorn
RUN pixi add gunicorn

# Set environment variables
ENV DATABASE_FILE=/app/storage/serverdatabase.db
ENV ENV=prod

# Use a production-ready server (gunicorn) to run the application
CMD pixi run populate && gunicorn -w 4 -b 0.0.0.0:5000 genaiserver_wl_folder.flask_app:app
