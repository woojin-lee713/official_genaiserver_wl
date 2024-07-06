# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Ensure the install_and_migrate.sh script is executable
RUN chmod +x ./install_and_migrate.sh

# Install dependencies using pixi and run database migrations
RUN ./install_and_migrate.sh

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["pixi", "run", "server"]
