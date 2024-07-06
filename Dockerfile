# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install pixi
RUN curl -fsSL https://get.pixi.dev/install.sh | sh

# Add pixi to PATH
ENV PATH="/root/.pixi/bin:$PATH"

# Install dependencies using pixi
RUN pixi install

# Initialize and run migrations
RUN pixi run init && pixi run migrate

# Expose the port the app runs on
EXPOSE 5000

# Run the app
CMD ["pixi", "run", "server"]
