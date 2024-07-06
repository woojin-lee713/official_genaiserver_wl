# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create and set the working directory
WORKDIR /app

# Copy pyproject.toml
COPY pyproject.toml /app/

# Install pixi
RUN pip install pixi

# Install dependencies
# RUN pixi install

# Copy the application code
COPY . /app

# Expose the port that the application runs on
EXPOSE 5000

# Populate the database
RUN pixi run populate

# Run the application
CMD ["pixi", "run", "server"]
