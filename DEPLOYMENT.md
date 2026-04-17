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

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)

---

## CI/CD với GitHub Actions

Project này có CI/CD pipeline tự động:

### 🚀 **Tự động deploy khi push lên main**

1. **Push code** lên GitHub main branch
2. **GitHub Actions** tự động:
   - Chạy tests (production readiness check)
   - Build Docker image
   - Deploy lên Railway
   - Health check sau deployment

### 🔧 **Setup GitHub Secrets**

Trong GitHub repository → Settings → Secrets and variables → Actions:

Thêm 2 secrets:

```
RAILWAY_TOKEN     → Railway CLI token (từ railway login --browserless)
RAILWAY_PROJECT_ID → Project ID (từ railway link)
```

**Cách lấy Railway token:**
```bash
railway login --browserless
# Copy token từ output
```

**Cách lấy Project ID:**
```bash
railway link
railway variables  # Project ID sẽ hiện trong list
```

### 📊 **Workflow Status**

Check CI/CD status: Repository → Actions tab

Workflow sẽ chạy khi:
- ✅ Push lên main/master branch
- ✅ Pull request vào main/master