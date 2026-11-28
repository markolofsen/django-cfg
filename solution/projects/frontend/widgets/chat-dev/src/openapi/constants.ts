// HTTP method colors mapping
export const HTTP_METHOD_COLORS = {
  GET: 'success',
  POST: 'primary',
  PUT: 'warning',
  DELETE: 'error',
  PATCH: 'default',
  HEAD: 'default',
  OPTIONS: 'default',
  TRACE: 'default',
} as const;

// HTTP status code colors mapping
export const HTTP_STATUS_COLORS = {
  '2': 'success',
  '3': 'default',
  '4': 'warning',
  '5': 'error',
} as const;

// Default request headers
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
} as const;

// Playground steps configuration
export const PLAYGROUND_STEPS = ['endpoints', 'request', 'response'] as const;

export const STEP_CONFIG = {
  endpoints: {
    title: 'API Endpoints',
    description: 'Browse and select API endpoints',
  },
  request: {
    title: 'Request Builder',
    description: 'Configure your API request',
  },
  response: {
    title: 'Response Viewer',
    description: 'View API response and details',
  },
} as const;
