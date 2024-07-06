# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the application code to the container
COPY . .

# Install pixi
RUN pip install pixi

# Copy the install and migrate script to the container
COPY install_and_migrate.sh .

# Make the script executable
RUN chmod +x install_and_migrate.sh

# Run the install and migrate script
RUN ./install_and_migrate.sh

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["pixi", "run", "server"]
