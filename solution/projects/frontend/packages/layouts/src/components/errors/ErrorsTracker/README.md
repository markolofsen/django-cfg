# Error Tracking System

**Universal error tracking for React apps with automatic toast notifications.**

## The Essence

One provider that listens to browser `CustomEvent`s from API client and shows toast notifications automatically:

```tsx
// Setup once
<ErrorTrackingProvider>
  <App />
</ErrorTrackingProvider>

// API client dispatches events
window.dispatchEvent(new CustomEvent('zod-validation-error', { detail: {...} }));
window.dispatchEvent(new CustomEvent('cors-error', { detail: {...} }));
window.dispatchEvent(new CustomEvent('network-error', { detail: {...} }));

// Provider catches them → shows toast → stores in state
const { errors } = useErrors();
```

## Quick Start

```tsx
import { ErrorTrackingProvider, useErrors } from '@djangocfg/layouts';

// 1. Wrap your app
<ErrorTrackingProvider
  validation={{ enabled: true, showToast: true }}
  cors={{ enabled: true, showToast: true }}
  network={{ enabled: false }}
>
  <App />
</ErrorTrackingProvider>

// 2. Access errors anywhere
function MyComponent() {
  const { errors, validationErrors, corsErrors, clearErrors } = useErrors();

  return <div>Total errors: {errors.length}</div>;
}
```

## Error Types

| Type | Event Name | Source | Toast Content |
|------|-----------|--------|---------------|
| **Validation** | `zod-validation-error` | API client Zod schema validation | Field errors, copy buttons |
| **CORS** | `cors-error` | API client CORS blocked | Causes, solutions, troubleshooting |
| **Network** | `network-error` | API client network issues | Error details, status code |

## Props

```tsx
<ErrorTrackingProvider
  validation={{
    enabled: true,           // Enable tracking
    showToast: true,         // Show toast
    maxErrors: 50,           // Max history
    duration: 8000,          // Toast duration (ms)
    showOperation: true,     // Show operation name
    showPath: true,          // Show API path
    showErrorCount: true,    // Show error count
    maxIssuesInToast: 3      // Max issues in toast
  }}
  cors={{
    enabled: true,
    showToast: true,
    duration: 0,             // 0 = no auto-dismiss
    showUrl: true,
    showMethod: true
  }}
  network={{
    enabled: false,          // Disabled by default
    showToast: true,
    showUrl: true,
    showMethod: true,
    showStatusCode: true
  }}
  onError={(error) => {
    // Custom handler
    // Return false to prevent toast
  }}
/>
```

## Structure

```
validation/
├── providers/ErrorTrackingProvider.tsx    # Single provider
├── components/
│   ├── ErrorToast.tsx                     # Universal toast
│   └── ErrorButtons.tsx                   # Copy buttons
├── utils/
│   ├── formatters.ts                      # Format errors
│   └── curl-generator.ts                  # Generate cURL
├── types.ts                               # TypeScript types
├── hooks.ts                               # useErrors()
└── index.ts                               # Public API
```

## How It Works

```
API Client (TypeScript)
    ↓
Throws Error
    ↓
Dispatches CustomEvent → window.dispatchEvent('zod-validation-error')
    ↓
ErrorTrackingProvider (React)
    ↓
Listens via window.addEventListener()
    ↓
1. Stores error in state
2. Shows toast notification
3. Provides via useErrors()
```

## Features

- ✅ **Single provider** for all error types
- ✅ **Automatic toast** notifications with copy buttons
- ✅ **Type-safe** TypeScript throughout
- ✅ **Theme-aware** buttons (no color issues)
- ✅ **Lucide icons** instead of emojis
- ✅ **Error history** with filtering by type
- ✅ **Custom handlers** for logging to Sentry/etc
- ✅ **SSR-safe** (checks `typeof window`)

## Migration from v1

```tsx
// Before
<ValidationErrorProvider>
  <CORSErrorProvider>
    <App />
  </CORSErrorProvider>
</ValidationErrorProvider>

// After
<ErrorTrackingProvider
  validation={{ ... }}
  cors={{ ... }}
>
  <App />
</ErrorTrackingProvider>

// Hooks
useValidationErrors() → useErrors().validationErrors
useCORSErrors() → useErrors().corsErrors
```

## API

### `useErrors()`

```tsx
const {
  errors,              // All errors
  validationErrors,    // Validation only
  corsErrors,          // CORS only
  networkErrors,       // Network only
  clearErrors,         // Clear all
  clearErrorsByType,   // Clear by type
  clearError,          // Clear one
  errorCount,          // Total count
  latestError,         // Latest error
  config               // Current config
} = useErrors();
```

### Event Details

```tsx
// Validation
{ type: 'validation', operation, path, method, error: ZodError, response, timestamp }

// CORS
{ type: 'cors', url, method, error: string, timestamp }

// Network
{ type: 'network', url, method, error: string, statusCode?, timestamp }
```

---

**Built with React Context + Browser CustomEvents**
