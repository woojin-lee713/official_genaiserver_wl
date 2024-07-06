# Use a base image that includes Node.js
FROM node:14

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install npm dependencies
RUN npm install

# Install pixi globally if referring to Pixijs CLI
RUN npm install -g pixi.js

# Copy the rest of the application code
COPY . .

# Install dependencies using pixi
RUN pixi install

# Initialize and run migrations (add any necessary commands here)
# RUN pixi run populate

# Expose the port your app runs on
EXPOSE 3000

# Command to run your application
CMD ["npm", "start"]
