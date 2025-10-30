# Docker Deployment Guide

This guide explains how to run the Resume Agent API using Docker and Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed (usually comes with Docker Desktop)
- `.env` file with your `OPENROUTER_API_KEY`

## Quick Start

### 1. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 2. Run with Docker Compose (Recommended)

**Start the application:**

```bash
docker-compose up -d
```

This will:
- Build the Docker image
- Start the container in detached mode
- Expose the API on `http://localhost:8000`

**View logs:**

```bash
docker-compose logs -f
```

**Stop the application:**

```bash
docker-compose down
```

**Restart the application:**

```bash
docker-compose restart
```

### 3. Verify It's Running

Visit the API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

Or use curl:

```bash
curl http://localhost:8000/health
```


### View Running Containers

```bash
docker ps
```

### View All Containers

```bash
docker ps -a
```

### View Logs

```bash
# Docker Compose
docker-compose logs -f

# Docker directly
docker logs -f resume-agent-api
```

### Execute Commands Inside Container

```bash
# Docker Compose
docker-compose exec resume-agent-api bash

# Docker directly
docker exec -it resume-agent-api bash
```

### Rebuild Image

```bash
# Docker Compose (rebuild and restart)
docker-compose up -d --build

# Docker directly
docker build -t resume-agent-api . --no-cache
```

### Remove Everything

```bash
# Stop and remove containers, networks
docker-compose down

# Also remove volumes
docker-compose down -v

# Remove image
docker rmi resume-agent-api
```

---

