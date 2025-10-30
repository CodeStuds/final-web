# Security Configuration

## API Keys and Tokens

This API uses environment variables for all sensitive credentials. **No API keys or tokens are sent through API requests.**

### Required Environment Variables

Set these in your `.env` file:

```bash
# Required: GitHub Personal Access Token
GITHUB_TOKEN=ghp_your_github_token_here

# Optional: Gemini API Key for AI-powered analysis
GEMINI_API_KEY=your_gemini_api_key_here
```

### Security Best Practices

1. **Never commit `.env` to version control**
   - The `.gitignore` file already excludes `.env`
   - Use `.env.example` as a template

2. **Keep tokens secure**
   - GitHub tokens: https://github.com/settings/tokens
   - Gemini API keys: https://makersuite.google.com/app/apikey
   - Rotate tokens regularly
   - Use minimum required permissions

3. **GitHub Token Permissions**
   Required scopes:
   - `repo` - Access repository data
   - `user` - Access user profile information

4. **API Request Format**
   The API does NOT accept tokens in requests:
   ```json
   {
     "github_profiles": ["username1", "username2"],
     "job_description": "Job requirements...",
     "use_gemini": true
   }
   ```

   ❌ **Old insecure format (removed):**
   ```json
   {
     "github_token": "ghp_...",  // DON'T DO THIS
     "gemini_api_key": "..."     // DON'T DO THIS
   }
   ```

5. **Environment Variable Loading**
   - Tokens are loaded from `.env` at startup (main.py:12)
   - Missing GITHUB_TOKEN will cause API to return 500 error
   - Missing GEMINI_API_KEY will disable AI features (graceful fallback)

### Deployment Considerations

When deploying to production:

1. **Use environment variables**
   ```bash
   export GITHUB_TOKEN="ghp_..."
   export GEMINI_API_KEY="..."
   ```

2. **Or use a secrets manager**
   - AWS Secrets Manager
   - Google Cloud Secret Manager
   - Azure Key Vault
   - HashiCorp Vault

3. **Never expose .env in production**
   - Set environment variables through hosting platform
   - Don't include .env in Docker images

4. **Rate Limiting**
   - GitHub API: 5,000 requests/hour (authenticated)
   - Gemini API: Check your quota at Google AI Studio
   - Consider implementing request caching

### Error Messages

If tokens are not configured:

```json
{
  "detail": "GITHUB_TOKEN not found in environment variables. Please set it in .env file"
}
```

This prevents the API from accidentally leaking token requirements or configurations.

### Monitoring

The API logs warnings for:
- Failed Gemini initialization (if key is invalid)
- GitHub API rate limit warnings
- Individual profile analysis failures

Tokens are never logged or exposed in error messages.
