# 🔐 Security Guide - HireSight

This document outlines security best practices, credential management, and deployment security for the HireSight platform.

---

## ⚠️ CRITICAL: Exposed Credentials

**If you've previously committed credentials to version control, they are compromised!**

### Immediate Actions Required:

1. **Rotate ALL exposed credentials immediately:**
   - Supabase API keys
   - Gemini API keys
   - GitHub tokens
   - Any other secrets

2. **Remove from git history:**
   ```bash
   # Use git-filter-repo to remove sensitive files from history
   # Install: pip install git-filter-repo

   git filter-repo --path DEVANGSHU_FRONTEND/supabase-config.js --invert-paths
   git filter-repo --path backend/api.py --invert-paths

   # Force push to remote (WARNING: This rewrites history!)
   git push origin --force --all
   ```

3. **Verify secrets are removed:**
   ```bash
   # Search for potential secrets
   git log -p | grep -i "api"
   git log -p | grep -i "key"
   ```

---

## 🔑 Credential Management

### 1. Environment Variables Setup

**Backend (.env file):**
```bash
cd backend
cp .env.example .env
# Edit .env with your actual credentials
nano .env
```

**Important fields:**
- `GEMINI_API_KEY` - Required for interview generation
- `GITHUB_TOKEN` - Optional but recommended (prevents rate limits)
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `API_KEYS` - Comma-separated list of API keys (if using authentication)

**Frontend:**

Create `env-config.js` for production deployment:
```javascript
window.ENV = {
  API_BASE_URL: 'https://your-api-domain.com/api',
  API_KEY: 'your-frontend-api-key',  // Only if API_KEYS_ENABLED=True
  SUPABASE_URL: 'https://your-project.supabase.co',
  SUPABASE_ANON_KEY: 'your-supabase-anon-key'
};
```

Include in HTML before other scripts:
```html
<script src="env-config.js"></script>
<script src="supabase-config.js"></script>
<script src="script.js"></script>
```

### 2. Generating Secure Keys

**Secret Key (Flask):**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**API Keys (for authentication):**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `read:user`, `repo` (read-only)
4. Copy token immediately (can't view again!)
5. Add to `.env`: `GITHUB_TOKEN=ghp_...`

**Gemini API Key:**
1. Visit https://aistudio.google.com/app/apikey
2. Create new API key
3. Set usage limits and restrictions
4. Add to `.env`: `GEMINI_API_KEY=AIza...`

---

## 🛡️ Security Features Implemented

### 1. Input Validation
- ✅ Job requirements validation (length limits, required fields)
- ✅ GitHub username format validation
- ✅ File type whitelist
- ✅ File size limits (50MB)

### 2. File Upload Security
- ✅ Secure filename sanitization
- ✅ ZIP bomb protection (200MB extracted limit, 100 files max)
- ✅ Directory traversal prevention
- ✅ File type validation (not just extension check)
- ✅ Automatic cleanup of temporary files

### 3. API Security
- ✅ Rate limiting (configurable per endpoint)
- ✅ Optional API key authentication
- ✅ CORS configuration
- ✅ Request logging with IP tracking

### 4. Logging & Monitoring
- ✅ Structured logging with timestamps
- ✅ Error tracking with stack traces
- ✅ Unauthorized access attempt logging
- ✅ File operations logging

---

## 🚀 Production Deployment Security Checklist

### Pre-Deployment

- [ ] **Set `DEBUG=False`** in `.env`
- [ ] **Rotate all credentials** (don't use development keys)
- [ ] **Enable API key authentication** (`API_KEYS_ENABLED=True`)
- [ ] **Generate strong secret keys** for all services
- [ ] **Configure CORS** with specific allowed origins
- [ ] **Set up HTTPS/TLS** (use Let's Encrypt)
- [ ] **Review .gitignore** - ensure no secrets committed
- [ ] **Scan for vulnerabilities**: `pip install safety && safety check`

### Infrastructure

- [ ] **Use environment variables** (not hardcoded configs)
- [ ] **Set up firewall rules** (only ports 80, 443, 22 open)
- [ ] **Enable fail2ban** for SSH protection
- [ ] **Configure nginx** as reverse proxy with rate limiting
- [ ] **Set up SSL certificates** (automatic renewal)
- [ ] **Use secrets management** (AWS Secrets Manager, HashiCorp Vault)

### Application

- [ ] **Enable rate limiting** on all public endpoints
- [ ] **Add request size limits** (prevent DoS)
- [ ] **Implement request timeouts** (30s max)
- [ ] **Set up error monitoring** (Sentry, Rollbar)
- [ ] **Configure log rotation** (logrotate)
- [ ] **Add health checks** for monitoring
- [ ] **Set file upload limits** in nginx/web server

### Database & Storage

- [ ] **Encrypt database connections** (SSL)
- [ ] **Regular database backups** (automated)
- [ ] **Encrypt sensitive data at rest**
- [ ] **Set up Redis** for session storage (optional)
- [ ] **Configure S3/object storage** for file uploads (production)

### Monitoring & Logging

- [ ] **Centralized logging** (ELK stack, CloudWatch)
- [ ] **Application monitoring** (New Relic, Datadog)
- [ ] **Set up alerts** for errors and unusual activity
- [ ] **Monitor rate limit violations**
- [ ] **Track API usage** per key

---

## 🔒 API Key Authentication

### Enabling Authentication

1. **Generate API keys:**
   ```bash
   python -c "import secrets; [print(secrets.token_urlsafe(32)) for _ in range(3)]"
   ```

2. **Add to `.env`:**
   ```bash
   API_KEYS_ENABLED=True
   API_KEYS=key1,key2,key3
   ```

3. **Distribute keys securely** (never via email/chat):
   - Use password manager links (1Password, LastPass)
   - Or encrypted communication channels

### Using API Keys

**Option 1: Header (Recommended)**
```bash
curl -H "X-API-Key: your-api-key" \
     -X POST http://localhost:5000/api/rank \
     -F "file=@resumes.zip" \
     -F "role=Developer" \
     -F "skills=Python,Flask"
```

**Option 2: Query Parameter**
```bash
curl -X POST "http://localhost:5000/api/rank?api_key=your-api-key" \
     -F "file=@resumes.zip" \
     -F "role=Developer"
```

**Frontend Integration:**
```javascript
const API_KEY = window.ENV.API_KEY;

fetch('/api/rank', {
  method: 'POST',
  headers: {
    'X-API-Key': API_KEY
  },
  body: formData
});
```

---

## 📋 Rate Limits

### Default Limits

| Endpoint | Limit | Reason |
|----------|-------|--------|
| `/api/health` | Unlimited | Health check |
| `/api/rank` | 10/min | Compute-intensive |
| `/api/analyze` | 15/min | File processing |
| `/api/github/analyze` | 20/min | External API |
| `/api/interview/generate` | 5/min | Paid API (Gemini) |
| `/api/leaderboard` | Default | Standard processing |

### Customizing Limits

Edit `backend/api.py`:
```python
@app.route('/api/rank', methods=['POST'])
@limiter.limit("20 per minute")  # Custom limit
def rank_candidates():
    # ...
```

Or configure in `.env`:
```bash
RATE_LIMIT_DEFAULT=100/hour,20/minute
```

---

## 🐛 Common Security Issues

### 1. CORS Errors in Production

**Problem:** Browser blocks requests due to CORS policy

**Solution:**
```python
# backend/api.py
from flask_cors import CORS

CORS(app, origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
])
```

### 2. File Upload Fails Silently

**Problem:** Files rejected without clear error

**Solution:** Check browser console and server logs:
```bash
tail -f backend/hiresight.log
```

Common causes:
- File too large (> 50MB)
- Invalid file type
- Rate limit exceeded

### 3. API Key Not Working

**Problem:** 401 Unauthorized even with API key

**Checklist:**
- [ ] `API_KEYS_ENABLED=True` in `.env`
- [ ] Key is in `API_KEYS` list
- [ ] No extra spaces in key
- [ ] Header format: `X-API-Key: yourkey` (no Bearer prefix)
- [ ] Backend restarted after `.env` changes

### 4. ZIP Extraction Fails

**Problem:** ZIP bomb or directory traversal detected

**Safe limits:**
- Max 100 files in ZIP
- Max 200MB extracted size
- No path traversal (`../` not allowed)

---

## 📊 Security Monitoring

### Log Analysis

**Check for unauthorized access attempts:**
```bash
grep "Unauthorized" backend/hiresight.log
```

**Monitor rate limit violations:**
```bash
grep "rate limit exceeded" backend/hiresight.log
```

**Track file uploads:**
```bash
grep "file uploaded" backend/hiresight.log | wc -l
```

### Alerting

Set up alerts for:
- Multiple failed authentication attempts
- Rate limit violations
- Large file uploads
- Unusual API usage patterns
- Error rate spikes

---

## 🔄 Credential Rotation Schedule

| Credential | Rotation Frequency | Priority |
|------------|-------------------|----------|
| API Keys | Every 90 days | High |
| Secret Key | Every 6 months | Medium |
| GitHub Token | Every 6 months | Medium |
| Gemini API Key | Every 6 months | Medium |
| Supabase Keys | On compromise only | High |

### Rotation Process

1. **Generate new credentials**
2. **Update `.env` files** (all environments)
3. **Restart services** with new credentials
4. **Test functionality** thoroughly
5. **Revoke old credentials** after 24-48 hours
6. **Update documentation** with rotation date

---

## 🆘 Incident Response

### If Credentials Are Compromised:

1. **Immediately rotate** all affected credentials
2. **Review logs** for unauthorized access
3. **Check billing** for unexpected usage
4. **Notify users** if data was accessed
5. **Document incident** and lessons learned
6. **Update security practices** to prevent recurrence

### If Under Attack:

1. **Enable CloudFlare** or similar DDoS protection
2. **Reduce rate limits** temporarily
3. **Block malicious IPs** in firewall
4. **Monitor resource usage** (CPU, memory, bandwidth)
5. **Scale up infrastructure** if needed
6. **Contact hosting provider** for assistance

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [API Security Checklist](https://github.com/shieldfy/API-Security-Checklist)
- [Supabase Security](https://supabase.com/docs/guides/platform/security)
- [GitHub Token Security](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

---

## ✅ Security Audit Checklist

Run this checklist quarterly or before major releases:

- [ ] All secrets removed from version control
- [ ] All dependencies up to date (`pip list --outdated`)
- [ ] No known vulnerabilities (`safety check`)
- [ ] Rate limiting tested and working
- [ ] File upload limits enforced
- [ ] Input validation comprehensive
- [ ] Logging capturing security events
- [ ] HTTPS/TLS certificates valid
- [ ] Backup and recovery tested
- [ ] Incident response plan updated

---

**Last Updated:** 2025-10-29
**Document Version:** 1.0
**Maintained By:** Development Team

For security concerns, contact: security@hiresight.example.com
