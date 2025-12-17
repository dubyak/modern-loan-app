# Supabase Setup

This directory contains the database schema and migrations for the Modern Loan App.

## Setup Instructions

### 1. Create a Supabase Project

1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Note down your project URL and anon/service keys

### 2. Run the Schema Migration

You have two options:

#### Option A: Using Supabase Dashboard (Easier)

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Create a new query
4. Copy and paste the contents of `schema.sql`
5. Run the query

#### Option B: Using Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

### 3. Configure Storage Buckets

Create storage buckets for file uploads:

1. Go to Storage in your Supabase dashboard
2. Create the following buckets:
   - `documents` (for user documents, IDs, business photos)
   - Make the bucket private (we'll use signed URLs)

3. Set up RLS policies for the storage bucket:

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

### 4. Configure Authentication

1. Go to Authentication > Providers in Supabase dashboard
2. Enable Phone authentication
3. Configure your SMS provider (Twilio, MessageBird, etc.)
4. Set up OTP settings:
   - OTP expiry: 5 minutes
   - OTP length: 6 digits

### 5. Environment Variables

Add these to your backend `.env` file:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
```

## Database Schema Overview

### Core Tables

- **users**: User accounts with roles (customer, agent, admin)
- **customer_profiles**: Business information for customers
- **loans**: Loan applications and their status
- **transactions**: Financial transactions (disbursements, repayments)
- **conversation_threads**: OpenAI conversation threads
- **messages**: Message history for conversations
- **documents**: Uploaded files and documents
- **otp_verifications**: OTP codes for phone verification

### Row Level Security (RLS)

All tables have RLS enabled with policies that:
- Allow users to view/edit their own data
- Allow admins and agents to view all data
- Protect sensitive information

## Maintenance

### Clean Up Expired OTPs

Run this periodically (or set up a cron job):

```sql
SELECT cleanup_expired_otps();
```

### Backup

Supabase automatically backs up your database. You can also:

1. Use `pg_dump` for manual backups
2. Set up automated backups via Supabase dashboard

## Testing

After running the migrations, you can test the schema with:

```sql
-- Create a test user
INSERT INTO auth.users (id, phone) VALUES (uuid_generate_v4(), '+254712345678');

-- Verify tables
SELECT * FROM public.users;
SELECT * FROM public.customer_profiles;
```
