FROM node:18-alpine as build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the files
COPY . .

# Build the application
RUN npm run build

# Use Node.js to serve the static files
FROM node:18-alpine as production

WORKDIR /app

# Install serve
RUN npm install -g serve

# Copy built files from the build stage
COPY --from=build /app/dist /app/dist

# Expose port
EXPOSE 3000

# Serve the application
CMD ["serve", "-s", "dist", "-l", "3000"] 