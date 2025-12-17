# CrisisFlow Deployment Guide

## Security Checklist

### ✅ Environment Variables
- [x] All API keys in `.env` files (never committed)
- [x] `.env.example` files for reference
- [x] SECRET_KEY validation (min 32 chars)
- [x] Frontend uses `NEXT_PUBLIC_*` prefix for public vars only

### ✅ CORS Configuration
- [x] CORS configured with environment-based allowed origins
- [x] Credentials allowed only for trusted origins
- [x] Specific methods and headers allowed

### ✅ Security Headers
- [x] X-Content-Type-Options: nosniff
- [x] X-Frame-Options: DENY
- [x] X-XSS-Protection: 1; mode=block
- [x] Strict-Transport-Security (HSTS)
- [x] Referrer-Policy
- [x] Permissions-Policy

### ✅ Authentication
- [x] JWT tokens with secure secret
- [x] Password hashing with bcrypt
- [x] Token expiration (30 days)

### ✅ Rate Limiting
- [x] Rate limiting middleware (can be enabled)
- [x] 60 requests per minute default

## Vercel Deployment

### Frontend (Next.js)

1. **Connect Repository**
   ```bash
   # Push to GitHub first
   git push origin main
   ```

2. **Import Project in Vercel**
   - Go to vercel.com
   - Import your GitHub repository
   - Select the `frontend` folder as root directory

3. **Environment Variables**
   Add these in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api.com
   NEXT_PUBLIC_WS_URL=wss://your-backend-api.com
   NEXT_PUBLIC_APP_NAME=CrisisFlow
   NEXT_PUBLIC_APP_ENV=production
   ```

4. **Build Settings**
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`

### Backend (FastAPI)

**Option 1: Railway / Render / Fly.io**
- Deploy FastAPI app
- Set environment variables from `.env.example`
- Update CORS `ALLOWED_ORIGINS` with Vercel URL

**Option 2: Vercel Serverless Functions**
- Convert FastAPI to serverless functions
- Use `vercel.json` configuration

**Required Environment Variables:**
```
SECRET_KEY=your-32-char-minimum-secret-key
DATABASE_URL=postgresql://...
ALLOWED_ORIGINS=https://your-frontend.vercel.app
OPENAI_API_KEY=...
GOOGLE_API_KEY=...
# ... other API keys
```

## Post-Deployment

1. **Update CORS Origins**
   - Add production frontend URL to `ALLOWED_ORIGINS`
   - Remove localhost in production

2. **Database Migration**
   - Run migrations if using Alembic
   - Or delete and recreate (dev only)

3. **Test Security**
   - Check security headers: https://securityheaders.com
   - Test CORS with production URLs
   - Verify API keys are not exposed

4. **Monitor**
   - Check error logs
   - Monitor rate limits
   - Watch for security issues

## Accessibility Checklist

- [x] Semantic HTML (main, aside, section, header)
- [x] ARIA labels on interactive elements
- [x] Keyboard navigation support
- [x] Focus indicators
- [x] Screen reader support (sr-only classes)
- [x] High contrast mode support
- [x] Reduced motion support
- [x] Responsive design

## Best Practices

1. **Never commit:**
   - `.env` files
   - API keys
   - Secrets
   - Database files

2. **Always use:**
   - Environment variables for config
   - HTTPS in production
   - Secure headers
   - Input validation
   - Rate limiting

3. **Regular updates:**
   - Dependencies
   - Security patches
   - API keys rotation

