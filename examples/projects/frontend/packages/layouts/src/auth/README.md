# 🔐 Auth Module Documentation

**Package**: @djangocfg/ui
**Module**: `/src/auth`
**Version**: 1.0.0

---

## 📋 Overview

Full-featured authentication module for Next.js applications with:
- OTP authentication (email/phone)
- React Context for state management
- Pre-built UI components
- Route protection (guards)
- API/media proxy middleware
- Full TypeScript support

**Architecture**: Context API + React Hooks + UI Components

---

## 📁 Module Structure

```
src/auth/
├── context/
│   ├── AuthContext.tsx           # Main auth context with logic
│   ├── types.ts                  # TypeScript types
│   └── index.ts                  # Exports
├── hooks/
│   ├── useAuthGuard.ts           # Route protection
│   ├── useAuthRedirect.ts        # Redirect management
│   ├── useAutoAuth.ts            # Auto-login
│   ├── useAuthForm.ts            # Form state
│   ├── useLocalStorage.ts        # localStorage hook
│   ├── useSessionStorage.ts      # sessionStorage hook
│   └── index.ts
├── components/
│   ├── AuthLayout/               # Complete Auth UI
│   │   ├── AuthLayout.tsx        # Main layout
│   │   ├── AuthContext.tsx       # Local context for form
│   │   ├── IdentifierForm.tsx    # Email/Phone input
│   │   ├── OTPForm.tsx           # OTP verification
│   │   ├── AuthHelp.tsx          # Help component
│   │   ├── types.ts
│   │   └── index.ts
│   ├── AuthDialog.tsx            # Modal for auth required
│   └── index.ts
├── middlewares/
│   ├── proxy.ts                  # Next.js middleware for /api/* and /media/*
│   └── index.ts
├── utils/
│   ├── validation.ts             # Email/OTP validation
│   ├── errors.ts                 # Error utilities
│   └── index.ts
└── index.ts                      # Main export
```

---

## 🚀 Quick Start

### 1. Setup AuthProvider

```tsx
// pages/_app.tsx
import { AuthProvider } from '@djangocfg/ui/auth';

export default function App({ Component, pageProps }) {
  return (
    <AuthProvider
      config={{
        apiUrl: process.env.NEXT_PUBLIC_API_URL,
        routes: {
          auth: '/auth',
          defaultCallback: '/dashboard',
          defaultAuthCallback: '/auth',
        },
      }}
    >
      <Component {...pageProps} />
    </AuthProvider>
  );
}
```

### 2. Create Auth Page

```tsx
// pages/auth.tsx
import { AuthLayout } from '@djangocfg/ui/auth';

export default function AuthPage() {
  return (
    <AuthLayout
      title="Welcome to Unrealon"
      subtitle="Sign in to continue"
      supportEmail="support@djangocfg.com"
      supportPhone="+1 (555) 123-4567"
    >
      {/* Optional: Custom header/footer */}
    </AuthLayout>
  );
}
```

### 3. Protect Routes

```tsx
// pages/dashboard.tsx
import { useAuthGuard } from '@djangocfg/ui/auth';

export default function Dashboard() {
  const { isAuthenticated, isLoading } = useAuthGuard({
    redirectTo: '/auth',
    requireAuth: true,
  });

  if (isLoading) return <div>Loading...</div>;

  return <div>Protected Dashboard</div>;
}
```

---

## 🧩 Core Components

### 1. AuthProvider %%PRIORITY:HIGH%%

**Purpose**: Main authentication context provider.

```tsx
import { AuthProvider } from '@djangocfg/ui/auth';

<AuthProvider config={authConfig}>
  {children}
</AuthProvider>
```

**Config Options**:

```typescript
interface AuthConfig {
  apiUrl?: string;                 // API base URL
  routes?: {
    auth?: string;                  // Auth page path (default: /auth)
    defaultCallback?: string;       // After login redirect (default: /dashboard)
    defaultAuthCallback?: string;   // After logout redirect (default: /auth)
  };
  onLogout?: () => void;            // Custom logout handler
  onConfirm?: (options) => Promise<{ confirmed: boolean }>;  // Custom confirm dialog
}
```

**Context Value**:

```typescript
interface AuthContextType {
  // State
  user: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Profile
  loadCurrentProfile: () => Promise<void>;
  checkAuthAndRedirect: () => Promise<void>;

  // Email Methods
  getSavedEmail: () => string | null;
  saveEmail: (email: string) => void;
  clearSavedEmail: () => void;

  // Phone Methods
  getSavedPhone: () => string | null;
  savePhone: (phone: string) => void;
  clearSavedPhone: () => void;

  // OTP Methods
  requestOTP: (identifier: string, channel?: 'email' | 'phone', sourceUrl?: string) => Promise<{
    success: boolean;
    message: string;
  }>;
  verifyOTP: (identifier: string, otpCode: string, channel?: 'email' | 'phone', sourceUrl?: string) => Promise<{
    success: boolean;
    message: string;
    user?: UserProfile;
  }>;
  refreshToken: () => Promise<{ success: boolean; message: string }>;
  logout: () => Promise<void>;

  // Redirect Methods
  getSavedRedirectUrl: () => string | null;
  saveRedirectUrl: (url: string) => void;
  clearSavedRedirectUrl: () => void;
  getFinalRedirectUrl: () => string;
  useAndClearRedirectUrl: () => string;
  saveCurrentUrlForRedirect: () => void;
}
```

---

### 2. AuthLayout %%PRIORITY:HIGH%%

**Purpose**: Pre-built UI for auth page with two-step flow.

```tsx
import { AuthLayout } from '@djangocfg/ui/auth';

<AuthLayout
  title="Welcome Back"
  subtitle="Sign in to your account"
  supportEmail="support@example.com"
  supportPhone="+1 234 567 8900"
  className="custom-class"
>
  {/* Optional custom content above forms */}
</AuthLayout>
```

**Props**:

```typescript
interface AuthProps {
  title?: string;              // Main title
  subtitle?: string;           // Subtitle text
  supportEmail?: string;       // Support email (shows help)
  supportPhone?: string;       // Support phone (shows help)
  className?: string;          // Custom CSS class
  children?: React.ReactNode;  // Custom content above forms
}
```

**Features**:
- ✅ Step 1: Email/Phone input with validation
- ✅ Step 2: OTP verification (6-digit code)
- ✅ Auto-redirect after successful auth
- ✅ Error handling with user-friendly messages
- ✅ Saved identifier (remembers email/phone)
- ✅ Support info display
- ✅ Fully styled with Tailwind CSS

**Flow**:

```
1. User enters email/phone
   → Validation
   → Save to localStorage
   → Call AuthContext.requestOTP()
   → Show success message

2. User enters OTP code
   → Validation (6 digits)
   → Call AuthContext.verifyOTP()
   → Save tokens (LocalStorage via @djangocfg/api)
   → Load user profile
   → Redirect to dashboard
```

---

### 3. AuthDialog %%PRIORITY:MEDIUM%%

**Purpose**: Modal dialog for "auth required" scenarios.

```tsx
import { AuthDialog, DIALOG_EVENTS } from '@djangocfg/ui/auth';

// In your app
<AuthDialog
  authPath="/auth"
  onAuthRequired={() => {
    // Custom handler
  }}
/>

// Trigger from anywhere
window.dispatchEvent(new CustomEvent(DIALOG_EVENTS.OPEN_AUTH_DIALOG, {
  detail: { message: 'Please sign in to access this feature' }
}));
```

**Events**:

```typescript
const DIALOG_EVENTS = {
  OPEN_AUTH_DIALOG: 'OPEN_AUTH_DIALOG',     // Open dialog
  CLOSE_AUTH_DIALOG: 'CLOSE_AUTH_DIALOG',   // Close dialog
  AUTH_SUCCESS: 'AUTH_SUCCESS',             // Auth successful
  AUTH_FAILURE: 'AUTH_FAILURE',             // Auth failed
};
```

**Usage Example**:

```tsx
// In a protected action
function handleProtectedAction() {
  if (!isAuthenticated) {
    window.dispatchEvent(new CustomEvent(DIALOG_EVENTS.OPEN_AUTH_DIALOG, {
      detail: { message: 'Sign in to save your work' }
    }));
    return;
  }

  // Continue with action
}
```

---

## 🪝 Hooks

### 1. useAuth() %%PRIORITY:HIGH%%

**Purpose**: Access AuthContext from any component.

```tsx
import { useAuth } from '@djangocfg/ui/auth';

function MyComponent() {
  const {
    user,
    isAuthenticated,
    isLoading,
    requestOTP,
    verifyOTP,
    logout
  } = useAuth();

  if (isLoading) return <div>Loading...</div>;

  if (!isAuthenticated) {
    return <button onClick={() => requestOTP(email)}>Sign In</button>;
  }

  return (
    <div>
      Welcome, {user?.email}
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

---

### 2. useAuthGuard() %%PRIORITY:HIGH%%

**Purpose**: Protect routes, auto-redirect unauthorized users.

```tsx
import { useAuthGuard } from '@djangocfg/ui/auth';

function ProtectedPage() {
  const { isAuthenticated, isLoading } = useAuthGuard({
    redirectTo: '/auth',      // Where to redirect if not authenticated
    requireAuth: true,        // Require authentication (default: true)
  });

  if (isLoading) return <div>Checking authentication...</div>;

  return <div>Protected content</div>;
}
```

**Options**:

```typescript
interface UseAuthGuardOptions {
  redirectTo?: string;    // Redirect path (default: '/auth')
  requireAuth?: boolean;  // Require auth (default: true)
}
```

---

### 3. useAuthRedirectManager() %%PRIORITY:MEDIUM%%

**Purpose**: Manage redirect URL after authentication.

```tsx
import { useAuthRedirectManager } from '@djangocfg/ui/auth';

function ProtectedRoute() {
  const {
    setRedirect,
    getFinalRedirectUrl,
    useAndClearRedirect
  } = useAuthRedirectManager({
    fallbackUrl: '/dashboard',
    clearOnUse: true
  });

  // Save current URL before redirect to auth
  useEffect(() => {
    if (!isAuthenticated) {
      setRedirect(window.location.pathname);
      router.push('/auth');
    }
  }, [isAuthenticated]);

  // After successful auth
  const handleLoginSuccess = () => {
    const redirectUrl = useAndClearRedirect();
    router.push(redirectUrl);  // Goes back to saved URL or fallback
  };
}
```

**Methods**:

```typescript
interface AuthRedirectManager {
  redirectUrl: string;
  setRedirect: (url: string) => void;
  getRedirect: () => string;
  clearRedirect: () => void;
  hasRedirect: () => boolean;
  getFinalRedirectUrl: () => string;          // Returns redirect or fallback
  useAndClearRedirect: () => string;          // Gets and clears redirect
}
```

---

### 4. useAutoAuth() %%PRIORITY:LOW%%

**Purpose**: Automatic authentication when tokens exist.

```tsx
import { useAutoAuth } from '@djangocfg/ui/auth';

function App() {
  useAutoAuth({
    enabled: true,                // Enable auto-auth
    redirectTo: '/dashboard',     // Where to redirect after auto-auth
    onSuccess: (user) => {
      console.log('Auto-auth successful:', user);
    },
    onFailure: () => {
      console.log('Auto-auth failed');
    }
  });

  return <div>App</div>;
}
```

---

### 5. useLocalStorage() & useSessionStorage() %%PRIORITY:LOW%%

**Purpose**: Type-safe storage hooks.

```tsx
import { useLocalStorage, useSessionStorage } from '@djangocfg/ui/auth';

function Component() {
  const [email, setEmail, removeEmail] = useLocalStorage<string>('saved_email', '');
  const [tempData, setTempData] = useSessionStorage<object>('temp_data', {});

  return (
    <div>
      <input value={email} onChange={(e) => setEmail(e.target.value)} />
      <button onClick={removeEmail}>Clear</button>
    </div>
  );
}
```

---

## 🛡️ Middleware

### Next.js Proxy Middleware %%PRIORITY:HIGH%%

**Purpose**: Proxy `/api/*` and `/media/*` to Django backend.

**Setup**:

```typescript
// middleware.ts (in your Next.js app root)
export { middleware, config } from '@djangocfg/ui/auth/middlewares';
```

**What it does**:

```typescript
// Proxies these patterns:
/api/*    → NEXT_PUBLIC_API_URL/api/*
/media/*  → NEXT_PUBLIC_API_URL/media/*

// Example:
// Request:  http://localhost:3000/api/auth/profile
// Proxies:  http://localhost:8000/api/auth/profile
```

**Why needed**:
- CORS bypass in development
- Unified URL structure
- Transparent access to Django API and media files

---

## 🔧 Utilities

### 1. Validation

```typescript
import { validateEmail, validateOTP } from '@djangocfg/ui/auth';

const isValidEmail = validateEmail('user@example.com');  // true
const isValidOTP = validateOTP('123456');                 // true
const isInvalidOTP = validateOTP('12345');                // false (not 6 digits)
```

### 2. Error Utilities

```typescript
import { formatAuthError, isNetworkError } from '@djangocfg/ui/auth/utils';

try {
  await authService.login();
} catch (error) {
  if (isNetworkError(error)) {
    alert('Network error, please try again');
  } else {
    alert(formatAuthError(error));
  }
}
```

---

## 📖 Usage Patterns

### Pattern 1: Simple Auth Page

```tsx
// pages/auth.tsx
import { AuthLayout } from '@djangocfg/ui/auth';

export default function AuthPage() {
  return <AuthLayout />;
}
```

**That's it!** You get a fully functional auth flow:
- Email/Phone input
- OTP verification
- Auto-redirect
- Error handling
- Saved identifier

---

### Pattern 2: Custom Auth Flow

```tsx
import { useAuth } from '@djangocfg/ui/auth';
import { useState } from 'react';

export default function CustomAuth() {
  const { requestOTP, verifyOTP } = useAuth();
  const [step, setStep] = useState<'email' | 'otp'>('email');
  const [email, setEmail] = useState('');
  const [otp, setOTP] = useState('');

  const handleRequestOTP = async () => {
    const result = await requestOTP(email);
    if (result.success) {
      setStep('otp');
    } else {
      alert(result.message);
    }
  };

  const handleVerifyOTP = async () => {
    const result = await verifyOTP(email, otp);
    if (result.success) {
      // User logged in, tokens saved, will auto-redirect
    } else {
      alert(result.message);
    }
  };

  if (step === 'email') {
    return (
      <div>
        <input value={email} onChange={(e) => setEmail(e.target.value)} />
        <button onClick={handleRequestOTP}>Send OTP</button>
      </div>
    );
  }

  return (
    <div>
      <input value={otp} onChange={(e) => setOTP(e.target.value)} />
      <button onClick={handleVerifyOTP}>Verify</button>
    </div>
  );
}
```

---

### Pattern 3: Protected Route

```tsx
// pages/dashboard.tsx
import { useAuthGuard } from '@djangocfg/ui/auth';

export default function Dashboard() {
  const { isLoading } = useAuthGuard();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  // If not authenticated, already redirected to /auth
  return <div>Welcome to Dashboard</div>;
}
```

---

### Pattern 4: Conditional UI

```tsx
import { useAuth } from '@djangocfg/ui/auth';

function Navigation() {
  const { isAuthenticated, user, logout } = useAuth();

  if (!isAuthenticated) {
    return <a href="/auth">Sign In</a>;
  }

  return (
    <div>
      <span>Welcome, {user?.email}</span>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

---

### Pattern 5: Auth Required Dialog

```tsx
// app.tsx
import { AuthDialog } from '@djangocfg/ui/auth';

function App() {
  return (
    <>
      <AuthDialog authPath="/auth" />
      {/* Rest of app */}
    </>
  );
}

// anywhere.tsx
import { DIALOG_EVENTS } from '@djangocfg/ui/auth';

function ProtectedAction() {
  const handleAction = () => {
    if (!isAuthenticated) {
      window.dispatchEvent(new CustomEvent(DIALOG_EVENTS.OPEN_AUTH_DIALOG, {
        detail: { message: 'Sign in to continue' }
      }));
      return;
    }

    // Perform action
  };
}
```

---

## 🔐 Security Features

### 1. Token Management

- ✅ Tokens stored in LocalStorage (via @djangocfg/api)
- ✅ Automatic injection in API requests
- ✅ Auto-refresh tokens
- ✅ Secure logout (tokens cleared)

### 2. Input Validation

- ✅ Email format validation
- ✅ Phone format validation (libphonenumber-js)
- ✅ OTP format validation (6 digits)
- ✅ XSS protection (React automatic)

### 3. CSRF Protection

- ✅ Django CSRF tokens via cookies
- ✅ credentials: 'include' in fetch requests
- ✅ Same-origin policy enforcement

### 4. Route Protection

- ✅ Server-side middleware (Next.js)
- ✅ Client-side guards (useAuthGuard)
- ✅ Auto-redirect unauthorized users

---

## 🎨 Styling

### Tailwind CSS Classes

All components use Tailwind CSS:

```tsx
// AuthLayout - Customizable
<AuthLayout className="bg-gradient-to-br from-blue-500 to-purple-600">
  {/* Custom content */}
</AuthLayout>

// Forms use these classes:
- bg-background
- text-foreground
- border-input
- text-destructive (errors)
- text-muted-foreground (help text)
```

### Dark Mode Support

```tsx
// Automatically respects next-themes
import { ThemeProvider } from 'next-themes';

<ThemeProvider attribute="class">
  <AuthProvider>
    <AuthLayout />
  </AuthProvider>
</ThemeProvider>
```

---

## 🧪 Testing

### Example: Test Auth Flow

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider, AuthLayout } from '@djangocfg/ui/auth';

test('auth flow works', async () => {
  const { getByPlaceholderText, getByText } = render(
    <AuthProvider>
      <AuthLayout />
    </AuthProvider>
  );

  // Step 1: Enter email
  const emailInput = getByPlaceholderText('Email or phone');
  fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
  fireEvent.click(getByText('Continue'));

  // Step 2: Enter OTP
  await waitFor(() => {
    expect(getByText('Enter verification code')).toBeInTheDocument();
  });

  const otpInput = getByPlaceholderText('000000');
  fireEvent.change(otpInput, { target: { value: '123456' } });
  fireEvent.click(getByText('Verify'));

  // Expect redirect or success
  await waitFor(() => {
    expect(window.location.pathname).toBe('/dashboard');
  });
});
```

---

## 🐛 Common Issues

### Issue 1: "Module not found" error

```bash
# Make sure @djangocfg/api is installed
pnpm add @djangocfg/api@workspace:*
```

### Issue 2: Infinite redirect loop

```typescript
// Check your routes config
<AuthProvider config={{
  routes: {
    auth: '/auth',               // Auth page path
    defaultCallback: '/dashboard', // After login
    defaultAuthCallback: '/auth'   // After logout
  }
}} />
```

### Issue 3: Tokens not persisting

```typescript
// Check if LocalStorageAdapter is configured in @djangocfg/api
import { api } from '@djangocfg/api';
console.log(api.isAuthenticated());  // Should return true after login
```

### Issue 4: CORS errors

```typescript
// Add middleware to proxy /api/*
// middleware.ts
export { middleware, config } from '@djangocfg/ui/auth/middlewares';
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Next.js App (Frontend)                   │  │
│  │                                                       │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │ AuthLayout │→ │ AuthContext  │→ │ @djangocfg/  │ │  │
│  │  │ (UI)       │  │ (State)      │  │ api         │ │  │
│  │  └────────────┘  └──────────────┘  └─────────────┘ │  │
│  │         ↓               ↓                  ↓         │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │          LocalStorage (Tokens)                 │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓ HTTP                            │
└───────────────────────────┼─────────────────────────────────┘
                            ↓
                    ┌───────────────┐
                    │ Next.js       │
                    │ Middleware    │
                    │ (Proxy)       │
                    └───────┬───────┘
                            ↓ /api/*, /media/*
                    ┌───────────────┐
                    │ Django API    │
                    │ Backend       │
                    └───────────────┘
```

---

## 🔗 Related Modules

- **@djangocfg/api** - API client with auth services
- **@djangocfg/ui/components** - UI components (Button, Dialog, etc)
- **@djangocfg/ui/hooks** - Utility hooks
- **next-themes** - Theme support
- **libphonenumber-js** - Phone validation

---

## 📝 TODO / Future Improvements

- [ ] Add biometric authentication support
- [ ] Social auth (Google, GitHub, etc)
- [ ] 2FA/MFA support
- [ ] Remember device functionality
- [ ] Session timeout warnings
- [ ] Magic link authentication
- [ ] SSR-compatible cookie auth
- [ ] Rate limiting for OTP requests

---

## 🎓 Best Practices

### 1. Always wrap app in AuthProvider

```tsx
// ✅ Good
<AuthProvider>
  <App />
</AuthProvider>

// ❌ Bad - hooks won't work
<App />
```

### 2. Use useAuthGuard for protected routes

```tsx
// ✅ Good - automatic redirect
function ProtectedPage() {
  useAuthGuard();
  return <div>Content</div>;
}

// ❌ Bad - manual checks everywhere
function ProtectedPage() {
  const { isAuthenticated } = useAuth();
  useEffect(() => {
    if (!isAuthenticated) router.push('/auth');
  }, [isAuthenticated]);
  // ...
}
```

### 3. Handle loading states

```tsx
// ✅ Good
function Dashboard() {
  const { isLoading, user } = useAuth();
  if (isLoading) return <Spinner />;
  return <div>Welcome {user?.email}</div>;
}

// ❌ Bad - might show undefined
function Dashboard() {
  const { user } = useAuth();
  return <div>Welcome {user.email}</div>;  // Error if user is null
}
```

### 4. Save redirect URL before auth

```tsx
// ✅ Good - user returns to intended page
function ProtectedRoute() {
  const { setRedirect } = useAuthRedirectManager();

  useEffect(() => {
    if (!isAuthenticated) {
      setRedirect(window.location.pathname);
      router.push('/auth');
    }
  }, []);
}
```

---

**Version**: 1.0.0
**Last Updated**: 2025-10-08
**Maintainer**: Reforms AI

---

**Tags**: `auth, authentication, otp, react, next.js, context, hooks, ui, middleware`
