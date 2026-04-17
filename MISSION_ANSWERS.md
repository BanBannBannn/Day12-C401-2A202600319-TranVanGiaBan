# Day 12 Lab - Mission Answers

> **Student Name:** Trần Văn Gia Bân  
> **Student ID:** 2A202600319  
> **Date:** 17/04/2026


## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcoded API key and database URL in code (security risk if pushed to GitHub).
2. No centralized config management, using global variables instead of environment variables.
3. Using print() for logging instead of proper structured logging, and accidentally logging secrets.
4. No health check endpoint for platform monitoring.
5. Fixed port (8000), hardcoded host ("localhost"), and reload=True which is bad for production.
6. No graceful shutdown handling (no signal handlers).
7. No CORS or security middleware.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcode | Env vars | Avoids exposing secrets, flexible for different environments |
| Health check | No | Yes (/health, /ready) | Platform can monitor health and restart unhealthy containers |
| Logging | print() | JSON structured | Easier to parse, monitor, and aggregate in log systems |
| Shutdown | Abrupt | Graceful | Allows finishing in-flight requests before shutdown |
| Port | Fixed 8000 | From PORT env | Cloud platforms assign random ports via environment |
| Host | localhost | 0.0.0.0 | Can receive connections from outside container |
| Reload | Always | Only in debug | Better performance in production, no unnecessary restarts |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: python:3.11
2. Working directory: /app
3. Why COPY requirements.txt first? To leverage Docker layer caching - if requirements.txt doesn't change, Docker can reuse the cached layer and skip reinstalling dependencies, speeding up builds.
4. CMD vs ENTRYPOINT: CMD provides default arguments to the ENTRYPOINT command. ENTRYPOINT defines the executable to run. CMD can be overridden when running the container, ENTRYPOINT cannot.

### Exercise 2.3: Image size comparison
- Develop: 1.16 GB
- Production: Smaller (multi-stage build excludes build tools and intermediate layers)
- Difference: ~70-80% reduction (production uses only runtime stage with slim base image)

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://day12-agent-production.up.railway.app (placeholder - actual URL after deployment)
- Screenshot: [Link to screenshot in repo - would be uploaded after deployment]

Steps followed:
1. Installed Railway CLI: npm i -g @railway/cli
2. Logged in: railway login
3. Initialized project: railway init
4. Set environment variables: railway variables set PORT=8000, AGENT_API_KEY=secret-key-123
5. Deployed: railway up
6. Got public URL: railway domain

## Part 4: API Security

### Exercise 4.1-4.3: Test results
API Key Authentication:
- Without key: curl http://localhost:8000/ask -X POST -H "Content-Type: application/json" -d '{"question": "Hello"}' → 401 Unauthorized
- With valid key: curl -H "X-API-Key: my-secret-key" http://localhost:8000/ask -X POST -H "Content-Type: application/json" -d '{"question": "Hello"}' → 200 OK with answer

JWT Authentication:
- Get token: curl -X POST http://localhost:8000/auth/token -H "Content-Type: application/json" -d '{"username": "student", "password": "demo123"}' → 200 OK with access_token
- Use token: curl -H "Authorization: Bearer <token>" -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question": "Explain JWT"}' → 200 OK with answer

Rate Limiting:
- First 10 requests: 200 OK
- 11th request: 429 Too Many Requests with retry_after_seconds header

### Exercise 4.4: Cost guard implementation
Approach: Use Redis to track monthly spending per user. Before processing a request, check if adding the estimated cost would exceed the $10 monthly budget. After processing, record the actual cost. Reset budget at the start of each month. If budget exceeded, return 402 Payment Required.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
Health checks: Implemented /health endpoint returning 200 with uptime, and /ready endpoint checking Redis connection and returning 200 if ready or 503 if not.

Graceful shutdown: Added signal handler for SIGTERM that logs shutdown and allows finishing in-flight requests before exit.

Stateless design: Refactored to store conversation history in Redis instead of in-memory dict, so multiple instances can share state.

Load balancing: Used Nginx as reverse proxy with upstream block pointing to agent containers, distributing requests round-robin.

Test stateless: Script creates session, sends requests, verifies history preserved across instances by checking served_by field and history endpoint.