# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the application code to the container
COPY . .

# Install dependencies
RUN pip install pixi

# Install dependencies using pixi
RUN pixi install

# Migrate the database
RUN pixi migrate

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["pixi", "run", "server"]
