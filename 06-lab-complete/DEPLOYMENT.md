# Deployment Information

## Public URL
https://deploy2-production-3023.up.railway.app

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://deploy2-production-3023.up.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://deploy2-production-3023.up.railway.app/ask \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT=8000
- AGENT_API_KEY=dev-key-change-me-in-production (change in production!)
- REDIS_URL (if using Redis)

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)