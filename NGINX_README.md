# Running SmartShelf with Nginx

This README explains how to run the SmartShelf application using Nginx as a reverse proxy.

## Setup Overview

The setup includes:
- Frontend: React application running on port 3000 (internal)
- Backend: FastAPI application running on port 8000 (internal)
- Nginx: Reverse proxy serving both frontend and backend on port 80
- Database: PostgreSQL running on port 5432

## Configuration Files

1. **docker-compose.yml**: Production configuration with Nginx
2. **docker-compose.dev.yml**: Development configuration with direct port mappings
3. **default.conf**: Nginx configuration file

## Running the Application

### Production Mode (with Nginx)

```bash
docker-compose up -d
```

This will start all services including Nginx. The application will be accessible at:
- http://localhost - Main application

### Development Mode (direct access)

```bash
docker-compose -f docker-compose.dev.yml up -d
```

This will start the services with direct port mappings. The application will be accessible at:
- http://localhost:3000 - Frontend
- http://localhost:8000 - Backend API

## Nginx Configuration Details

The Nginx configuration handles the following routes:
- `/` - Routes to the frontend (React application)
- `/api/*` - Routes to the backend API
- `/health` - Routes to the backend health check endpoint

## Troubleshooting

If you encounter issues:

1. Check container logs:
   ```bash
   docker-compose logs nginx
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. Verify the Nginx configuration:
   ```bash
   docker-compose exec nginx nginx -t
   ```

3. Check connectivity between services:
   ```bash
   docker-compose exec nginx curl -I backend:8000/health
   docker-compose exec nginx curl -I frontend:3000
   ``` 