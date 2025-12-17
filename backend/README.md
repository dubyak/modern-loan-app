# Modern Loan App - Backend API

FastAPI backend for the Modern Loan App microfinance platform.

## Features

- **Authentication**: Phone number + password with OTP verification
- **AI Loan Officer**: OpenAI Assistant integration (Lucy)
- **Loan Management**: Calculate, create, and manage loans
- **Transaction Tracking**: Track disbursements and repayments
- **Document Upload**: Supabase Storage integration
- **Role-Based Access**: Customer, Agent, and Admin roles
- **RESTful API**: Comprehensive API with OpenAPI docs

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT + Supabase Auth
- **AI**: OpenAI Assistant API
- **Storage**: Supabase Storage
- **Deployment**: Railway

## Getting Started

### Prerequisites

- Python 3.11+
- Supabase account
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Set up Supabase**
   - Follow instructions in `../supabase/README.md`
   - Run the schema migration
   - Create storage buckets

### Running Locally

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at http://localhost:8000

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/send-otp` - Send OTP code
- `POST /api/auth/verify-otp` - Verify OTP code

### Users
- `GET /api/users/me` - Get current user
- `PUT /api/users/me` - Update current user
- `GET /api/users/me/profile` - Get user profile
- `PUT /api/users/me/profile` - Update user profile

### Loans
- `POST /api/loans/calculate` - Calculate loan offer
- `POST /api/loans` - Create loan application
- `GET /api/loans` - Get user's loans
- `GET /api/loans/{id}` - Get specific loan
- `POST /api/loans/{id}/accept` - Accept loan offer
- `PUT /api/loans/{id}/status` - Update loan status (admin/agent)

### Transactions
- `GET /api/transactions` - Get user's transactions
- `GET /api/transactions/{id}` - Get specific transaction

### AI/Chat
- `POST /api/ai/chat` - Chat with Lucy (AI loan officer)
- `GET /api/ai/thread` - Get or create conversation thread
- `GET /api/ai/thread/history` - Get conversation history

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - Get user's documents
- `GET /api/documents/{id}` - Get specific document
- `DELETE /api/documents/{id}` - Delete document

### Admin
- `GET /api/admin/users` - List all users
- `GET /api/admin/users/{id}` - Get specific user
- `GET /api/admin/users/{id}/profile` - Get user's profile
- `GET /api/admin/loans` - List all loans
- `GET /api/admin/stats` - Get platform statistics
- `PUT /api/admin/users/{id}/status` - Update user status

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # API route handlers
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── loans.py
│   │       ├── transactions.py
│   │       ├── ai.py
│   │       ├── documents.py
│   │       └── admin.py
│   ├── auth/                # Authentication utilities
│   │   ├── dependencies.py
│   │   └── utils.py
│   ├── models/              # Pydantic schemas
│   │   └── schemas.py
│   ├── services/            # Business logic
│   │   └── ai_assistant.py
│   ├── config.py            # Configuration
│   └── database.py          # Database client
├── main.py                  # Application entry point
├── requirements.txt         # Dependencies
└── .env.example             # Environment variables template
```

## Deployment to Railway

1. **Connect repository to Railway**
   - Go to Railway dashboard
   - Create new project
   - Connect your GitHub repository
   - Select the `backend` directory as root

2. **Set environment variables**
   - Copy all variables from `.env.example`
   - Set them in Railway dashboard

3. **Deploy**
   - Railway will automatically detect the Python app
   - It will install dependencies and start the server

## Environment Variables

See `.env.example` for all required environment variables.

**Critical Variables:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service role key
- `OPENAI_API_KEY` - OpenAI API key
- `JWT_SECRET_KEY` - Secret key for JWT tokens (change in production!)

## Development

### Code Style

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

### Testing

```bash
# Run tests (when implemented)
pytest
```

## Lucy - The AI Loan Officer

Lucy is powered by OpenAI's Assistant API and handles:
- Customer onboarding
- Business information collection
- Loan eligibility assessment
- Loan offer calculation and presentation
- Loan acceptance/rejection

The AI assistant is configured with specific instructions to:
- Use simple language (2nd-3rd grade reading level)
- Be warm and encouraging
- Assess business viability
- Make informed lending decisions

## Security

- All routes except `/auth/register`, `/auth/login`, and `/loans/calculate` require authentication
- JWT tokens expire after 24 hours
- Row-level security (RLS) enabled on Supabase
- File uploads are validated for type and size
- Password hashing with bcrypt
- OTP codes expire after 5 minutes

## License

MIT
