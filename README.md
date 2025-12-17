# Modern Loan App

An AI-powered microfinance platform for providing loans to microentrepreneurs. This is a modern replica of the Magical Loan App, rebuilt with Next.js, FastAPI, and deployed on Railway.

## Overview

This platform features "Lucy," an AI loan officer powered by OpenAI's GPT-4, that conducts conversational loan underwriting through a chat interface. The system handles the complete loan lifecycle from registration through disbursement and repayment tracking.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Next.js 15     │─────▶│  FastAPI        │─────▶│   Supabase      │
│  Frontend       │      │  Backend        │      │   PostgreSQL    │
│  (Railway)      │      │  (Railway)      │      │                 │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                │
                                │
                                ▼
                         ┌─────────────────┐
                         │   OpenAI API    │
                         │   (GPT-4)       │
                         │   Lucy AI       │
                         └─────────────────┘
```

### Tech Stack

**Frontend:**
- Next.js 15 (App Router)
- React 19
- TypeScript
- Tailwind CSS
- Zustand (state management)
- Axios (HTTP client)

**Backend:**
- Python 3.11+
- FastAPI
- OpenAI Assistant API
- Supabase Python Client
- JWT Authentication

**Database & Services:**
- Supabase (PostgreSQL + Auth + Storage)
- OpenAI GPT-4
- Railway (deployment)

## Features

### Core Features

- **AI Loan Officer ("Lucy")**: Conversational AI that interviews customers, evaluates businesses, and makes lending decisions
- **Multi-Role System**: Customer, Agent, and Admin interfaces with role-based access control
- **Complete Loan Lifecycle**: From application through disbursement and repayment tracking
- **Document Management**: Upload and store IDs, business photos, and supporting documents
- **Transaction History**: Complete audit trail of all financial transactions
- **Real-time Chat**: Streaming responses from AI with conversation history
- **Phone Authentication**: OTP-based verification for security

### User Workflows

**Customer Journey:**
1. Register with phone number
2. Verify via OTP
3. Chat with Lucy about business
4. Receive loan offer
5. Accept/reject loan
6. Track repayments

**Agent Portal:**
- Register new customers
- View customer details
- Manage loan applications
- Review documents

**Admin Dashboard:**
- Monitor all users
- View platform statistics
- Manage loan portfolio
- User administration

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Supabase account
- OpenAI API key
- Railway account (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd modern-loan-app
   ```

2. **Set up Supabase**
   ```bash
   # Follow instructions in supabase/README.md
   # Run the schema migration
   ```

3. **Start Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Copy and configure .env
   cp .env.example .env
   # Edit .env with your credentials

   # Run server
   uvicorn main:app --reload
   ```

   Backend will be available at http://localhost:8000
   API docs at http://localhost:8000/docs

4. **Start Frontend**
   ```bash
   cd frontend
   npm install

   # Copy and configure .env
   cp .env.example .env.local
   # Edit .env.local with backend URL

   # Run dev server
   npm run dev
   ```

   Frontend will be available at http://localhost:3000

## Project Structure

```
modern-loan-app/
├── frontend/              # Next.js frontend application
│   ├── src/
│   │   ├── app/          # Next.js pages (App Router)
│   │   ├── lib/          # Utilities and API client
│   │   ├── store/        # Zustand stores
│   │   └── components/   # React components
│   ├── public/           # Static assets
│   └── package.json
│
├── backend/               # FastAPI backend application
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── auth/         # Authentication
│   │   ├── models/       # Pydantic schemas
│   │   └── services/     # Business logic (AI assistant)
│   ├── main.py           # Application entry point
│   └── requirements.txt
│
├── supabase/              # Database schema and migrations
│   ├── schema.sql        # Complete database schema
│   └── README.md         # Setup instructions
│
├── docs/                  # Documentation
├── DEPLOYMENT.md          # Deployment guide
└── README.md             # This file
```

## Environment Variables

### Backend `.env`

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_ASSISTANT_ID=  # Auto-created on first run
OPENAI_MODEL=gpt-4-turbo-preview

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend `.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment instructions to Railway.

### Quick Deploy to Railway

1. **Create Railway project** and connect GitHub repo
2. **Create two services**: frontend (root: `frontend`) and backend (root: `backend`)
3. **Set environment variables** as shown above
4. **Deploy** - Railway auto-detects and builds both services

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/send-otp` - Send OTP code
- `POST /api/auth/verify-otp` - Verify OTP

**AI Chat:**
- `POST /api/ai/chat` - Chat with Lucy
- `GET /api/ai/thread` - Get conversation thread
- `GET /api/ai/thread/history` - Get chat history

**Loans:**
- `POST /api/loans/calculate` - Calculate loan offer
- `POST /api/loans` - Create loan application
- `GET /api/loans` - Get user's loans
- `POST /api/loans/{id}/accept` - Accept loan

See backend README for complete API documentation.

## Lucy - The AI Loan Officer

Lucy is powered by OpenAI's Assistant API with custom instructions to:

- Use simple, accessible language (2nd-3rd grade reading level)
- Be warm, encouraging, and culturally sensitive
- Interview customers about their business
- Assess business viability
- Make informed lending decisions
- Calculate and present loan offers

### AI Functions

Lucy can call these functions:
1. `calculate_loan_offer` - Calculate loan terms
2. `store_customer_acceptance` - Save loan acceptance
3. `get_loan_info` - Retrieve loan and transaction history
4. `complete_onboarding` - Mark onboarding complete

## Database Schema

The Supabase PostgreSQL database includes:

**Core Tables:**
- `users` - User accounts with roles
- `customer_profiles` - Business information
- `loans` - Loan applications and status
- `transactions` - Financial transactions
- `conversation_threads` - AI chat threads
- `messages` - Chat message history
- `documents` - Uploaded files
- `otp_verifications` - OTP codes

**Security:**
- Row Level Security (RLS) enabled on all tables
- Users can only access their own data
- Admins/agents have elevated permissions

See `supabase/schema.sql` for complete schema.

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uvicorn main:app --reload

# Run tests (TODO)
pytest

# Format code
black .
```

### Frontend Development

```bash
cd frontend

# Run dev server
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Lint code
npm run lint
```

## Testing

### Manual Testing

1. **Register** a new user
2. **Login** with credentials
3. **Chat with Lucy** - Try asking for a loan
4. **Upload documents** - Test file upload
5. **View transactions** - Check loan history

### API Testing

Use the Swagger UI at `/docs` to test endpoints directly.

## Differences from Original App

This modern replica improves upon the original:

| Feature | Original | Modern Replica |
|---------|----------|----------------|
| Frontend | Streamlit | Next.js 15 + React 19 |
| Backend | Monolithic Streamlit | FastAPI (separate service) |
| Database | Backend microservice | Supabase (direct access) |
| Deployment | K8s + Jenkins | Railway (simplified) |
| Storage | AWS S3 | Supabase Storage |
| Messaging | WhatsApp integration | Removed (manual handling) |
| Scheduler | APScheduler | Removed for v1 |

## Roadmap

- [ ] Complete Agent portal UI
- [ ] Complete Admin dashboard
- [ ] Add real-time notifications
- [ ] Implement loan repayment tracking
- [ ] Add scheduled messaging
- [ ] SMS/WhatsApp integration
- [ ] M-Pesa integration (for Kenya)
- [ ] Analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Multi-language support (Swahili)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Security

- Never commit `.env` files
- Keep Supabase service_role key secret
- Use strong JWT secrets in production
- Enable 2FA on all service accounts
- Regularly update dependencies
- Monitor OpenAI API usage

## License

MIT License - see LICENSE file

## Support

For issues and questions:
- Check the documentation
- Review API docs at `/docs`
- Check Railway logs for errors
- Review Supabase configuration

## Acknowledgments

- Original Magical Loan App team
- OpenAI for GPT-4 API
- Supabase for database infrastructure
- Railway for deployment platform
- Vercel for Next.js framework

---

**Built with ❤️ for microentrepreneurs**
