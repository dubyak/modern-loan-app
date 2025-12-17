# Railway Deployment Guide

Complete step-by-step guide to deploy both frontend and backend to Railway.

## Overview

This monorepo contains two separate services:
- **Backend**: FastAPI (Python) in `backend/` directory
- **Frontend**: Next.js in `frontend/` directory

Railway requires each service to be deployed separately.

## Step 1: Set Up Supabase

Before deploying to Railway, set up your Supabase database:

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Run the database migration from `supabase/schema.sql`
3. Create storage bucket named `documents`
4. Copy your credentials (URL, anon key, service key)

## Step 2: Deploy Backend to Railway

### 2.1 Create Backend Service

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `modern-loan-app` repository
4. Railway will try to auto-detect and fail - that's expected

### 2.2 Configure Backend Service

1. **Set Root Directory**:
   - Click on your service
   - Go to "Settings"
   - Find "Root Directory"
   - Set to: `backend`

2. **Set Build & Start Commands** (Settings → Deploy):
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Health Check**:
   - Health Check Path: `/health`
   - Health Check Timeout: 100

### 2.3 Set Backend Environment Variables

Go to "Variables" tab and add:

```bash
# Application
APP_NAME=Modern Loan App API
ENVIRONMENT=production
DEBUG=False

# CORS - Update after frontend is deployed
CORS_ORIGINS=["https://your-frontend.up.railway.app"]

# Supabase (from Step 1)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here
SUPABASE_ANON_KEY=your-anon-key-here

# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_ASSISTANT_ID=
OPENAI_MODEL=gpt-4-turbo-preview

# JWT - IMPORTANT: Generate a strong secret!
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters-long-use-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OTP Settings
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=5

# Loan Settings
DEFAULT_INTEREST_RATE=15.0
MIN_LOAN_AMOUNT=1000.0
MAX_LOAN_AMOUNT=50000.0
DEFAULT_LOAN_TENURE_DAYS=30

# File Upload
MAX_FILE_SIZE_MB=10
```

### 2.4 Deploy Backend

1. Click "Deploy"
2. Wait for deployment to complete
3. Check logs for any errors
4. Visit `https://your-backend.up.railway.app/health` to verify
5. Visit `https://your-backend.up.railway.app/docs` to see API documentation

### 2.5 Get Backend URL

Copy your backend URL (e.g., `https://modern-loan-app-backend-production.up.railway.app`)

You'll need this for the frontend.

## Step 3: Deploy Frontend to Railway

### 3.1 Create Frontend Service

1. In the same Railway project, click "New Service"
2. Select "GitHub Repo"
3. Select the same `modern-loan-app` repository

### 3.2 Configure Frontend Service

1. **Set Root Directory**:
   - Go to "Settings"
   - Find "Root Directory"
   - Set to: `frontend`

2. **Commands** (Railway should auto-detect Next.js):
   - **Build Command**: `npm run build`
   - **Start Command**: `npm start`

If not auto-detected, set manually in Settings.

### 3.3 Set Frontend Environment Variables

Go to "Variables" tab and add:

```bash
# API Backend - Use URL from Step 2.5
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app

# Supabase (same as backend)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

### 3.4 Deploy Frontend

1. Click "Deploy"
2. Wait for build to complete (may take 2-3 minutes)
3. Visit your frontend URL

### 3.5 Get Frontend URL

Copy your frontend URL (e.g., `https://modern-loan-app-frontend-production.up.railway.app`)

## Step 4: Update Backend CORS

Now that you have the frontend URL, update the backend:

1. Go to Backend service
2. Go to "Variables"
3. Update `CORS_ORIGINS`:
   ```bash
   CORS_ORIGINS=["https://your-frontend.up.railway.app"]
   ```
4. The backend will auto-redeploy

## Step 5: Test the Application

1. Visit your frontend URL
2. Click "Register" and create an account
3. Login
4. Test the chat with Lucy
5. Check that everything works

## Step 6: Set Up Custom Domains (Optional)

### Backend Domain

1. Go to Backend service → Settings → Networking
2. Click "Generate Domain" or "Custom Domain"
3. Add your custom domain (e.g., `api.yourdomain.com`)
4. Update DNS records as shown
5. Update frontend `NEXT_PUBLIC_API_URL`

### Frontend Domain

1. Go to Frontend service → Settings → Networking
2. Add custom domain (e.g., `app.yourdomain.com`)
3. Update DNS records
4. Update backend `CORS_ORIGINS`

## Troubleshooting

### Backend Issues

**Build Fails:**
- Check Python version (should be 3.11+)
- Verify all environment variables are set
- Check logs for missing dependencies

**Health Check Fails:**
- Verify start command includes `--host 0.0.0.0 --port $PORT`
- Check `/health` endpoint returns 200

**Database Connection Errors:**
- Verify Supabase credentials
- Check Supabase project is active
- Test connection from local environment first

### Frontend Issues

**Build Fails:**
- Check Node version (should be 18+)
- Verify `package.json` is correct
- Check build logs for errors

**API Connection Issues:**
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend CORS includes frontend URL
- Test backend endpoint directly

**White Screen/404:**
- Check build completed successfully
- Verify start command is `npm start`
- Check browser console for errors

### Common Errors

**Error: "Railway could not determine how to build"**
- Make sure Root Directory is set to `backend` or `frontend`
- Verify build/start commands are set

**CORS Error in Browser:**
- Update backend `CORS_ORIGINS` with exact frontend URL
- Include protocol (`https://`)
- Redeploy backend after updating

**OpenAI API Errors:**
- Verify API key is valid
- Check billing is enabled
- Monitor rate limits

## Monitoring

### Check Logs

- Backend logs: Backend service → Logs
- Frontend logs: Frontend service → Logs
- Look for errors, warnings

### Monitor Resources

- CPU usage
- Memory usage
- Build time
- Response time

### Set Up Alerts (Optional)

Railway Pro plan includes:
- Uptime monitoring
- Error alerts
- Resource alerts

## Cost Optimization

**Free Tier:**
- $5 free credit per month
- Enough for development/testing

**Estimated Monthly Costs:**
- Backend: $5-10/month
- Frontend: $5-10/month
- Total: ~$10-20/month for both services

**Tips to Reduce Costs:**
- Use smaller instance sizes during development
- Set up auto-sleep for non-production environments
- Monitor usage regularly

## Environment-Specific Deployments

### Development Environment

Create separate services for dev:
1. Deploy from `develop` branch
2. Use different Supabase project
3. Set `ENVIRONMENT=development`
4. Use test OpenAI key

### Production Environment

1. Deploy from `main` branch
2. Use production Supabase
3. Set `DEBUG=False`
4. Use production OpenAI key
5. Enable logging/monitoring

## Next Steps

After successful deployment:

1. ✅ Test all features thoroughly
2. ✅ Create first admin user in Supabase
3. ✅ Set up monitoring/alerts
4. ✅ Configure custom domains
5. ✅ Set up backup strategy
6. ✅ Document any customizations

## Support

If you encounter issues:

1. Check Railway logs
2. Review environment variables
3. Test locally first
4. Check Railway status page
5. Contact Railway support (Pro plan)

## Security Checklist

Before going live:

- [ ] `JWT_SECRET_KEY` is strong and random
- [ ] `DEBUG=False` in production
- [ ] Supabase service_role key is secret
- [ ] CORS only allows your frontend domain
- [ ] All secrets are in environment variables (not in code)
- [ ] HTTPS is enabled (automatic with Railway)
- [ ] Database RLS policies are enabled
- [ ] Storage buckets are properly secured

## Updating the Application

### Deploy Updates

1. Push changes to GitHub
2. Railway auto-deploys (if enabled)
3. Or manually trigger deployment

### Rolling Back

1. Go to service → Deployments
2. Click on previous successful deployment
3. Click "Redeploy"

Good luck with your deployment! 🚀
