# @djangocfg/api

Type-safe API client for backend integration.

## What's Inside

- Auto-generated TypeScript clients
- Type-safe request/response handling
- Error handling utilities

## Usage

```tsx
import { apiClient } from '@djangocfg/api';

// Make API calls
const response = await apiClient.get('/endpoint');
const data = await apiClient.post('/endpoint', { body });
```

## Features

- **Type Safety** - Full TypeScript support
- **Auto-generated** - Clients generated from OpenAPI spec
- **Error Handling** - Consistent error responses
- **Authentication** - Token management built-in

## Configuration

Set API base URL via environment variable:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Generation

To regenerate clients from OpenAPI spec:

```bash
pnpm generate
```
