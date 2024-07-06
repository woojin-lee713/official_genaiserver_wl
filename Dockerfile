FROM ghcr.io/prefix-dev/pixi:latest

WORKDIR /app
COPY . /app

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Install necessary Python packages including Cython and Wheel first
RUN pip3 install cython wheel

# Copy requirements.txt and install necessary Python packages
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

# Install pixi dependencies
RUN pixi install

# Set environment variables
ENV DATABASE_FILE=/app/storage/serverdatabase.db
ENV ENV=prod

# Ensure the storage directory exists
RUN mkdir -p /app/storage

CMD pixi run populate && gunicorn genaiserver_wl_folder.flask_app:app --bind 0.0.0.0:5000
