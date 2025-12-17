# Modern Loan App - Frontend

Next.js 15 frontend for the Modern Loan App microfinance platform.

## Features

- **Modern UI**: Built with Next.js 15, React 19, and Tailwind CSS
- **AI Chat Interface**: Real-time chat with Lucy, the AI loan officer
- **Multi-Role Support**: Customer, Agent, and Admin interfaces
- **Authentication**: JWT-based auth with local storage
- **Responsive Design**: Mobile-first responsive design
- **State Management**: Zustand for global state
- **Form Handling**: React Hook Form with Zod validation
- **Type Safety**: Full TypeScript support

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **UI**: React 19, Tailwind CSS, Lucide Icons
- **State**: Zustand
- **Forms**: React Hook Form + Zod
- **HTTP**: Axios
- **Deployment**: Railway

## Getting Started

### Prerequisites

- Node.js 18+
- Backend API running (see `../backend/README.md`)

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API URL and Supabase credentials
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   - Navigate to http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/                # Next.js App Router pages
│   │   ├── page.tsx        # Homepage
│   │   ├── layout.tsx      # Root layout
│   │   ├── globals.css     # Global styles
│   │   ├── login/          # Login page
│   │   ├── register/       # Registration page
│   │   ├── customer/       # Customer dashboard (chat)
│   │   ├── agent/          # Agent portal (TODO)
│   │   └── admin/          # Admin dashboard (TODO)
│   ├── lib/                # Utilities
│   │   └── api.ts          # API client
│   ├── store/              # State management
│   │   └── authStore.ts    # Auth state (Zustand)
│   └── components/         # Reusable components (TODO)
├── public/                 # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
└── railway.json           # Railway deployment config
```

## Available Scripts

```bash
# Development
npm run dev          # Start dev server (http://localhost:3000)

# Production
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
```

## Key Features

### 1. Homepage
- Landing page with features and how-it-works section
- Auto-redirect authenticated users to their dashboard

### 2. Authentication
- **Login**: Phone number + password
- **Register**: Create new account with phone verification
- **JWT Tokens**: Stored in localStorage
- **Auto-redirect**: Based on user role

### 3. Customer Dashboard
- **AI Chat Interface**: Real-time chat with Lucy
- **Conversation History**: Persistent chat history
- **Loan Management**: View and accept loan offers
- **Document Upload**: Upload business photos and IDs

### 4. Agent Portal (TODO)
- View all customers
- Manage loan applications
- Review documents

### 5. Admin Dashboard (TODO)
- Platform statistics
- User management
- Loan oversight
- System configuration

## API Integration

The frontend communicates with the backend via REST API:

```typescript
// Example: Login
import { authAPI } from '@/lib/api';

const response = await authAPI.login({
  phone: '+254712345678',
  password: 'password123'
});

// Example: Chat with AI
import { aiAPI } from '@/lib/api';

const response = await aiAPI.chat({
  message: 'I need a loan for my business',
  thread_id: 'optional-thread-id'
});
```

## State Management

Using Zustand for auth state:

```typescript
import { useAuthStore } from '@/store/authStore';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuthStore();

  // Use auth state and methods
}
```

## Styling

Tailwind CSS with custom components:

```tsx
// Button styles
<button className="btn btn-primary">Primary Button</button>
<button className="btn btn-secondary">Secondary Button</button>

// Input styles
<input className="input" />

// Card styles
<div className="card">Card content</div>
```

## Deployment to Railway

### Method 1: Via Railway Dashboard

1. **Create new project** on Railway
2. **Connect GitHub repository**
3. **Select frontend directory** as root
4. **Set environment variables**:
   - `NEXT_PUBLIC_API_URL` - Your backend API URL
   - `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key

5. **Deploy** - Railway auto-detects Next.js and deploys

### Method 2: Via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

## Environment Variables

```bash
# API Backend
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Supabase (for direct access if needed)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Development Tips

### Hot Reload
Next.js supports fast refresh. Changes to components will hot reload automatically.

### Type Safety
Always define TypeScript interfaces for API responses:

```typescript
interface User {
  id: string;
  phone: string;
  role: 'customer' | 'agent' | 'admin';
  // ...
}
```

### Error Handling
The API client automatically handles 401 errors and redirects to login.

### Custom Hooks
Create custom hooks for common operations:

```typescript
// hooks/useLoans.ts
export function useLoans() {
  const [loans, setLoans] = useState([]);

  useEffect(() => {
    // Fetch loans
  }, []);

  return { loans };
}
```

## TODO / Future Enhancements

- [ ] Complete Agent portal UI
- [ ] Complete Admin dashboard
- [ ] Add document upload UI
- [ ] Implement real-time notifications
- [ ] Add loan calculator widget
- [ ] Transaction history UI
- [ ] Profile management page
- [ ] Dark mode support
- [ ] PWA support
- [ ] i18n (Swahili translation)

## Troubleshooting

### CORS Errors
Make sure the backend CORS_ORIGINS includes your frontend URL.

### API Connection Failed
1. Check backend is running
2. Verify NEXT_PUBLIC_API_URL is correct
3. Check network tab for actual error

### Build Errors
```bash
# Clear .next cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## License

MIT
