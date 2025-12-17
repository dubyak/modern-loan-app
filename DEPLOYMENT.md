# Deployment Guide

Complete guide for deploying the Modern Loan App to production.

## Prerequisites

Before deploying, ensure you have:

1. **Supabase Account** - [Sign up at supabase.com](https://supabase.com)
2. **OpenAI API Key** - [Get from platform.openai.com](https://platform.openai.com)
3. **Railway Account** - [Sign up at railway.app](https://railway.app)
4. **GitHub Repository** - Code pushed to GitHub

## Step 1: Set Up Supabase

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose organization and set project name
4. Set a strong database password
5. Choose a region close to your users (e.g., Singapore for Kenya)
6. Click "Create new project"

### 1.2 Run Database Migrations

1. Go to SQL Editor in Supabase dashboard
2. Copy contents of `supabase/schema.sql`
3. Paste into SQL Editor
4. Click "Run" to execute the migration
5. Verify tables were created in Table Editor

### 1.3 Create Storage Buckets

1. Go to Storage in Supabase dashboard
2. Click "New bucket"
3. Name it `documents`
4. Set to **Private** bucket
5. Click "Create bucket"

### 1.4 Set Up Storage Policies

In SQL Editor, run:

```sql
-- Allow users to upload their own documents
CREATE POLICY "Users can upload own documents"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Allow users to view their own documents
CREATE POLICY "Users can view own documents"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Allow admins and agents to view all documents
CREATE POLICY "Admins and agents can view all documents"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'documents' AND
    EXISTS (
        SELECT 1 FROM public.users
        WHERE id = auth.uid() AND role IN ('admin', 'agent')
    )
);
```

### 1.5 Configure Authentication

1. Go to Authentication → Providers
2. Enable **Phone** authentication
3. Configure SMS provider (optional for development):
   - Twilio
   - MessageBird
   - Or use test mode
4. Set OTP settings:
   - OTP expiry: 300 seconds (5 minutes)
   - OTP length: 6 digits

### 1.6 Get API Keys

1. Go to Project Settings → API
2. Copy:
   - **Project URL** (`SUPABASE_URL`)
   - **anon/public key** (`SUPABASE_ANON_KEY`)
   - **service_role key** (`SUPABASE_SERVICE_KEY`) - Keep this secret!

## Step 2: Get OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign in or create account
3. Go to API Keys section
4. Click "Create new secret key"
5. Name it "Modern Loan App"
6. Copy the key (you won't see it again!)
7. Add billing information if not already done

## Step 3: Deploy Backend to Railway

### 3.1 Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your repository
5. Select your `modern-loan-app` repository

### 3.2 Configure Backend Service

1. Railway should detect the Python app
2. If not, set root directory to `backend`
3. Go to Settings:
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4`
   - **Build Command**: `pip install -r requirements.txt`

### 3.3 Set Environment Variables

In Railway dashboard, go to Variables tab and add:

```bash
# Application
APP_NAME=Modern Loan App API
ENVIRONMENT=production
DEBUG=False

# CORS - Add your frontend domain
CORS_ORIGINS=["https://your-frontend.railway.app"]

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here
SUPABASE_ANON_KEY=your-anon-key-here

# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_ASSISTANT_ID=
OPENAI_MODEL=gpt-4-turbo-preview

# JWT Authentication - Generate a strong random key!
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters-long
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

### 3.4 Deploy Backend

1. Click "Deploy"
2. Wait for build to complete
3. Check logs for any errors
4. Visit `https://your-backend.railway.app/health` to verify
5. Visit `https://your-backend.railway.app/docs` to see API docs

### 3.5 Get Backend URL

Copy your backend URL (e.g., `https://modern-loan-app-backend.railway.app`)

## Step 4: Deploy Frontend to Railway

### 4.1 Create Frontend Service

1. In same Railway project, click "New Service"
2. Select "GitHub Repo"
3. Select same repository
4. Set root directory to `frontend`

### 4.2 Configure Frontend Service

Railway should auto-detect Next.js. If not:

- **Build Command**: `npm run build`
- **Start Command**: `npm start`

### 4.3 Set Environment Variables

```bash
# API Backend URL
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

### 4.4 Deploy Frontend

1. Click "Deploy"
2. Wait for build to complete
3. Visit your frontend URL
4. Test the application

## Step 5: Post-Deployment Configuration

### 5.1 Update Backend CORS

Go back to backend environment variables and update `CORS_ORIGINS`:

```bash
CORS_ORIGINS=["https://your-frontend.railway.app","https://your-custom-domain.com"]
```

Redeploy backend.

### 5.2 Create Admin User

You need to manually create the first admin user:

1. Register a normal user through the UI
2. Go to Supabase → Table Editor → users
3. Find your user
4. Change `role` from `customer` to `admin`
5. Save changes

Now you can access the admin dashboard.

### 5.3 Test OpenAI Assistant

The OpenAI Assistant (Lucy) will be automatically created on first use. Check logs:

```
Created new assistant: asst_xxxxxxxxxxxxxxx
```

Copy this assistant ID and add it to backend environment variables:

```bash
OPENAI_ASSISTANT_ID=asst_xxxxxxxxxxxxxxx
```

This prevents creating a new assistant each time the app restarts.

## Step 6: Custom Domain (Optional)

### 6.1 Railway Custom Domains

1. Go to Frontend service → Settings → Domains
2. Click "Add Custom Domain"
3. Enter your domain (e.g., `app.yourdomain.com`)
4. Add DNS records as shown:
   - Type: CNAME
   - Name: app (or @)
   - Value: [railway provided value]

5. Wait for DNS propagation (5-60 minutes)
6. Railway will auto-provision SSL certificate

### 6.2 Update Environment Variables

Update both frontend and backend with your custom domain:

**Backend** `CORS_ORIGINS`:
```bash
CORS_ORIGINS=["https://app.yourdomain.com"]
```

**Frontend** remains the same (uses relative URLs)

## Step 7: Monitoring & Maintenance

### 7.1 Check Logs

Monitor Railway logs regularly:
- Backend logs for API errors
- Frontend logs for build issues
- Look for OpenAI API errors

### 7.2 Monitor Costs

Keep an eye on:
- **OpenAI Usage**: Check usage dashboard
- **Supabase**: Free tier has limits
- **Railway**: $5/month + resource usage

### 7.3 Database Maintenance

Run periodically:

```sql
-- Clean up expired OTPs
SELECT cleanup_expired_otps();

-- Check database size
SELECT pg_size_pretty(pg_database_size(current_database()));
```

### 7.4 Backup Strategy

Supabase automatically backs up your database. You can also:
1. Go to Database → Backups
2. Enable Point-in-Time Recovery (paid)
3. Schedule manual backups

## Troubleshooting

### Backend won't start
- Check Python version (3.11+)
- Verify all environment variables are set
- Check logs for missing dependencies

### Frontend can't connect to backend
- Verify NEXT_PUBLIC_API_URL is correct
- Check backend CORS settings
- Verify backend is running

### OpenAI errors
- Verify API key is valid
- Check billing is enabled
- Monitor rate limits

### Database connection issues
- Verify Supabase URL and keys
- Check Supabase project is running
- Verify RLS policies are correct

### File upload fails
- Check Supabase storage bucket exists
- Verify storage policies are set
- Check file size limits

## Security Checklist

- [ ] JWT_SECRET_KEY is strong and random (32+ characters)
- [ ] Supabase service_role key is secret (never in frontend)
- [ ] DEBUG=False in production
- [ ] CORS only allows your domains
- [ ] Supabase RLS policies are enabled
- [ ] Storage buckets are private
- [ ] Environment variables are not in git
- [ ] HTTPS is enabled (Railway does this automatically)
- [ ] OpenAI API key is restricted to your project

## Cost Estimation

**Monthly costs** (estimated):

- **Railway**: $5-20/month (2 services)
- **Supabase**: Free tier OK for small usage, $25+/month for production
- **OpenAI**: Varies based on usage (~$0.01-0.03 per conversation)
- **Domain** (optional): ~$10-15/year

**Total**: ~$5-50/month depending on scale

## Next Steps

After deployment:

1. Test all features thoroughly
2. Set up monitoring/alerting
3. Configure SMS provider for OTP
4. Add custom domain
5. Set up analytics
6. Create user documentation
7. Plan for scaling

## Support

If you encounter issues:

1. Check logs in Railway dashboard
2. Review environment variables
3. Verify Supabase configuration
4. Check GitHub issues
5. Review API documentation at `/docs`

Good luck with your deployment! 🚀
