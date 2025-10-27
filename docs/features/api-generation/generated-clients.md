---
title: Using Generated Clients
sidebar_position: 4
keywords:
  - django-cfg generated clients
  - django generated clients
  - generated clients django-cfg
description: Generated API client examples for TypeScript, Python, and JavaScript. Type-safe client libraries with automatic validation and error handling.
---

# Using Generated Clients

After generating clients with `python manage.py generate`, you'll have type-safe TypeScript and Python clients ready to use in your applications.

## TypeScript Clients

### Installation

Generated TypeScript clients are organized by zone group:

- **CFG zones**: `openapi/clients/typescript/cfg/{zone_name}/`
- **Custom zones**: `openapi/clients/typescript/custom/{zone_name}/`

:::info Zone Grouping
Zones starting with `cfg_` (like `cfg_support`, `cfg_payments`) are grouped under `cfg/`, while custom zones (like `public`, `admin`, `mobile`) are under `custom/`.
:::

#### Copy to Your Project

```bash
# Copy specific CFG zone
cp -r openapi/clients/typescript/cfg/cfg_support src/api/

# Copy specific custom zone
cp -r openapi/clients/typescript/custom/public src/api/

# Or copy all zones (both cfg and custom)
cp -r openapi/clients/typescript/* src/api/
```

#### Install as NPM Package

Create a package:

```json
// package.json
{
  "name": "@myorg/api-client",
  "version": "1.0.0",
  "main": "index.ts",
  "types": "index.ts"
}
```

Then install locally or publish to NPM.

### Basic Usage

```typescript
import API from './api/cfg_support';

// Initialize client
const api = new API('https://api.example.com');

// Set authentication
api.setToken('access-token', 'refresh-token');

// Make API calls (all methods are fully typed)
const tickets = await api.listTickets();
const ticket = await api.getTicket({ id: '123' });
const newTicket = await api.createTicket({
  title: 'Issue with payment',
  description: 'Cannot process refund',
  priority: 'high'
});
```

### Authentication

#### Bearer Token

```typescript
// Set access and refresh tokens
api.setToken('access-token', 'refresh-token');

// Check if authenticated
if (api.isAuthenticated()) {
  console.log('User is logged in');
}

// Clear tokens
api.clearToken();
```

#### API Key

```typescript
// Set API key
api.setApiKey('your-api-key');
```

#### Custom Headers

```typescript
// Add custom headers
api.setHeaders({
  'X-Custom-Header': 'value',
  'X-Request-ID': 'unique-id'
});
```

### Multiple Zones

Use clients from different zones together:

```typescript
// Import CFG zones (built-in Django-CFG apps)
import SupportAPI from './api/cfg/cfg_support';
import AccountsAPI from './api/cfg/cfg_accounts';
import KnowbaseAPI from './api/cfg/cfg_knowbase';

// Import custom zones (your project-specific apps)
import PublicAPI from './api/custom/public';
import AdminAPI from './api/custom/admin';

const support = new SupportAPI('https://api.example.com');
const accounts = new AccountsAPI('https://api.example.com');
const knowbase = new KnowbaseAPI('https://api.example.com');
const publicApi = new PublicAPI('https://api.example.com');
const adminApi = new AdminAPI('https://api.example.com');

// Share authentication across clients
const token = 'access-token';
support.setToken(token);
accounts.setToken(token);
knowbase.setToken(token);
adminApi.setToken(token);
// publicApi doesn't need auth (public zone)

// Use each client independently
const user = await accounts.getProfile();
const tickets = await support.listTickets();
const docs = await knowbase.searchDocuments({ query: 'API' });
const products = await publicApi.listProducts();  // No auth needed
const analytics = await adminApi.getAnalytics();  // Admin only
```

### React Integration

```typescript
import { useState, useEffect } from 'react';
import API from './api/cfg_support';

function TicketList() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const api = new API(process.env.REACT_APP_API_URL);
    api.setToken(localStorage.getItem('access_token'));

    api.listTickets()
      .then(data => {
        setTickets(data.results);
        setLoading(false);
      })
      .catch(error => {
        console.error('Failed to load tickets:', error);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <ul>
      {tickets.map(ticket => (
        <li key={ticket.id}>{ticket.title}</li>
      ))}
    </ul>
  );
}
```

### Vue Integration

```vue
<template>
  <div>
    <div v-if="loading">Loading...</div>
    <ul v-else>
      <li v-for="ticket in tickets" :key="ticket.id">
        {{ ticket.title }}
      </li>
    </ul>
  </div>
</template>

<script>
import API from './api/cfg_support';

export default {
  data() {
    return {
      tickets: [],
      loading: true,
    };
  },
  async mounted() {
    const api = new API(process.env.VUE_APP_API_URL);
    api.setToken(localStorage.getItem('access_token'));

    try {
      const data = await api.listTickets();
      this.tickets = data.results;
    } catch (error) {
      console.error('Failed to load tickets:', error);
    } finally {
      this.loading = false;
    }
  },
};
</script>
```

### Error Handling

```typescript
try {
  const ticket = await api.createTicket({
    title: 'Bug report',
    description: 'Found a critical bug'
  });
  console.log('Ticket created:', ticket.id);
} catch (error) {
  if (error.response) {
    // API error response
    console.error('Status:', error.response.status);
    console.error('Data:', error.response.data);
  } else if (error.request) {
    // No response received
    console.error('No response from server');
  } else {
    // Other errors
    console.error('Error:', error.message);
  }
}
```

## Python Clients

### Installation

Generated Python clients are organized by zone group:

- **CFG zones**: `openapi/clients/python/cfg/{zone_name}/`
- **Custom zones**: `openapi/clients/python/custom/{zone_name}/`

:::info Zone Grouping
Python packages follow the same grouping as TypeScript:
- CFG zones: `cfg_support`, `cfg_payments`, etc.
- Custom zones: `public`, `admin`, etc.
:::

#### Install Locally

```bash
# Install specific CFG zone
pip install -e openapi/clients/python/cfg/cfg_support

# Install specific custom zone
pip install -e openapi/clients/python/custom/public

# Or add to requirements.txt
echo "-e openapi/clients/python/cfg/cfg_support" >> requirements.txt
echo "-e openapi/clients/python/custom/public" >> requirements.txt
```

#### Publish to PyPI

Package and publish:

```bash
cd openapi/clients/python/cfg_support
python -m build
python -m twine upload dist/*
```

### Basic Usage

```python
from cfg_support import Client
from cfg_support.api.default import (
    list_tickets,
    get_ticket,
    create_ticket
)
from cfg_support.models import TicketCreate

# Initialize client
client = Client(base_url="https://api.example.com")
client = client.with_headers({
    "Authorization": "Bearer access-token"
})

# Synchronous API calls
tickets = list_tickets.sync(client=client)
print(f"Found {len(tickets.results)} tickets")

ticket = get_ticket.sync(id="123", client=client)
print(f"Ticket: {ticket.title}")

# Create ticket
new_ticket_data = TicketCreate(
    title="Bug report",
    description="Found a critical bug",
    priority="high"
)
new_ticket = create_ticket.sync(
    client=client,
    json_body=new_ticket_data
)
print(f"Created ticket: {new_ticket.id}")
```

### Async Usage

```python
import asyncio
from cfg_support import Client
from cfg_support.api.default import (
    list_tickets,
    create_ticket
)

async def main():
    client = Client(base_url="https://api.example.com")
    client = client.with_headers({
        "Authorization": "Bearer access-token"
    })

    # Async API calls
    tickets = await list_tickets.asyncio(client=client)
    print(f"Found {len(tickets.results)} tickets")

    new_ticket = await create_ticket.asyncio(
        client=client,
        json_body={"title": "Test", "description": "Testing"}
    )
    print(f"Created: {new_ticket.id}")

# Run async code
asyncio.run(main())
```

### Authentication

```python
# Bearer token
client = client.with_headers({
    "Authorization": f"Bearer {access_token}"
})

# API key
client = client.with_headers({
    "X-API-Key": "your-api-key"
})

# Custom headers
client = client.with_headers({
    "X-Custom-Header": "value",
    "X-Request-ID": "unique-id"
})
```

### Multiple Zones

```python
# Import CFG zones (built-in Django-CFG apps)
from cfg_support import Client as SupportClient
from cfg_accounts import Client as AccountsClient
from cfg_knowbase import Client as KnowbaseClient

# Import custom zones (your project-specific apps)
from public import Client as PublicClient
from admin import Client as AdminClient

# Initialize clients
support = SupportClient(base_url="https://api.example.com")
accounts = AccountsClient(base_url="https://api.example.com")
knowbase = KnowbaseClient(base_url="https://api.example.com")
public = PublicClient(base_url="https://api.example.com")
admin = AdminClient(base_url="https://api.example.com")

# Share authentication (for authenticated zones)
headers = {"Authorization": "Bearer access-token"}
support = support.with_headers(headers)
accounts = accounts.with_headers(headers)
knowbase = knowbase.with_headers(headers)
admin = admin.with_headers(headers)
# public client doesn't need auth (public zone)

# Use each client
from cfg_support.api.default import list_tickets
from cfg_accounts.api.default import get_profile
from cfg_knowbase.api.default import search_documents
from public.api.default import list_products
from admin.api.default import get_analytics

tickets = list_tickets.sync(client=support)
user = get_profile.sync(client=accounts)
docs = search_documents.sync(client=knowbase, query="API")
products = list_products.sync(client=public)  # No auth needed
analytics = get_analytics.sync(client=admin)  # Admin only
```

### Django Integration

```python
# views.py
from django.http import JsonResponse
from cfg_support import Client
from cfg_support.api.default import list_tickets

def get_user_tickets(request):
    """Get tickets for current user"""
    # Create API client
    client = Client(base_url="https://api.example.com")
    client = client.with_headers({
        "Authorization": f"Bearer {request.user.access_token}"
    })

    # Fetch tickets
    try:
        tickets = list_tickets.sync(
            client=client,
            user_id=request.user.id
        )
        return JsonResponse({
            'tickets': [ticket.dict() for ticket in tickets.results]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from cfg_support import Client
from cfg_support.api.default import list_tickets

app = FastAPI()

def get_api_client():
    """Dependency to get API client"""
    client = Client(base_url="https://api.example.com")
    return client.with_headers({
        "Authorization": "Bearer service-token"
    })

@app.get("/tickets")
async def get_tickets(client: Client = Depends(get_api_client)):
    """Get all tickets"""
    tickets = await list_tickets.asyncio(client=client)
    return {"tickets": [ticket.dict() for ticket in tickets.results]}
```

### Error Handling

```python
from httpx import HTTPStatusError

try:
    ticket = create_ticket.sync(
        client=client,
        json_body={"title": "Test"}
    )
except HTTPStatusError as e:
    print(f"HTTP {e.response.status_code}: {e.response.text}")
except Exception as e:
    print(f"Error: {e}")
```

## Protocol Buffer/gRPC Clients

Django-CFG can generate Protocol Buffer definitions and gRPC service definitions from your OpenAPI specification. This is useful when you need high-performance RPC communication or want to use gRPC instead of REST.

:::info Compilation Required
Proto files must be compiled with `protoc` before use. Each generated group includes a README.md with detailed compilation instructions for Python, Go, TypeScript, and other languages.
:::

### Installation

Install gRPC tools for your language:

#### Python
```bash
pip install grpcio grpcio-tools
```

#### Go
```bash
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

#### TypeScript
```bash
npm install ts-proto
```

### Generating Proto Files

```bash
# Generate Protocol Buffers for specific group
python manage.py generate_client \
  --openapi-files openapi/groups/profiles.yaml \
  --output-dir openapi/clients \
  --group profiles \
  --proto --no-python --no-typescript --no-go

# Or generate all clients including proto
python manage.py generate_api  # Proto enabled by default
```

### Compilation

Proto files must be compiled to your target language:

#### Python
```bash
cd openapi/clients/proto/profiles
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. api__profiles/*.proto
```

#### Go
```bash
cd openapi/clients/proto/profiles
protoc -I. --go_out=. --go-grpc_out=. api__profiles/*.proto
```

#### TypeScript
```bash
cd openapi/clients/proto/profiles
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. api__profiles/*.proto
```

See the generated `README.md` in each proto group for complete compilation instructions.

### Basic Usage (Python)

```python
import grpc
from profiles.api__profiles import service_pb2, service_pb2_grpc

# Create insecure channel (for development)
channel = grpc.insecure_channel('localhost:50051')

# Create service stub
stub = service_pb2_grpc.ProfilesServiceStub(channel)

# List profiles
request = service_pb2.ProfilesProfilesListRequest(
    page=1,
    page_size=10
)
response = stub.ProfilesProfilesList(request)

print(f"Found {response.data.count} profiles")
for profile in response.data.results:
    print(f"- {profile.user.email}: {profile.bio}")

# Create profile
create_request = service_pb2.ProfilesProfilesCreateRequest(
    body=service_pb2.Userprofilerequest(
        bio="Software Engineer",
        location="San Francisco, CA",
        website="https://example.com"
    )
)
new_profile = stub.ProfilesProfilesCreate(create_request)
print(f"Created profile for {new_profile.data.user.email}")
```

### Basic Usage (Go)

```go
package main

import (
    "context"
    "fmt"
    "log"
    "google.golang.org/grpc"
    pb "your-module/profiles/api__profiles"
)

func main() {
    // Create connection
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatalf("did not connect: %v", err)
    }
    defer conn.Close()

    // Create client
    client := pb.NewProfilesServiceClient(conn)

    // List profiles
    resp, err := client.ProfilesProfilesList(context.Background(), &pb.ProfilesProfilesListRequest{
        Page:     proto.Int64(1),
        PageSize: proto.Int64(10),
    })
    if err != nil {
        log.Fatalf("could not list: %v", err)
    }

    fmt.Printf("Found %d profiles\n", resp.Data.Count)
    for _, profile := range resp.Data.Results {
        fmt.Printf("- %s: %s\n", profile.User.Email, profile.Bio)
    }
}
```

### Authentication

gRPC uses interceptors for authentication instead of HTTP headers:

```python
import grpc

# Create credentials interceptor
class AuthInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self, token):
        self._token = token

    def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        metadata.append(('authorization', f'Bearer {self._token}'))

        new_details = client_call_details._replace(metadata=metadata)
        return continuation(new_details, request)

# Use interceptor
channel = grpc.insecure_channel('localhost:50051')
intercepted_channel = grpc.intercept_channel(channel, AuthInterceptor('your-token'))
stub = service_pb2_grpc.ProfilesServiceStub(intercepted_channel)
```

### Error Handling

gRPC uses status codes instead of HTTP status codes:

```python
import grpc

try:
    response = stub.ProfilesProfilesRetrieve(request)
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
        print("Profile not found")
    elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
        print("Permission denied")
    else:
        print(f"RPC failed: {e.code()}: {e.details()}")
```

### Features

- ✅ **Type-safe messages** - Proto3 message definitions with full type safety
- ✅ **gRPC services** - Complete gRPC service definitions with all operations
- ✅ **Multi-language support** - Compile to Python, Go, TypeScript, C++, Java, Rust, etc.
- ✅ **Binary serialization** - Efficient Protocol Buffer encoding
- ✅ **Cross-platform** - Works with any gRPC implementation
- ✅ **All OpenAPI features** - Enums, arrays, nested objects, pagination

### Generated Files

For each service, the proto generator creates:

```
openapi/clients/proto/profiles/
├── api__profiles/
│   ├── messages.proto          # Message definitions (models, enums)
│   ├── service.proto           # gRPC service and RPC methods
│   ├── messages_pb2.py         # Compiled Python messages
│   ├── messages_pb2_grpc.py    # Empty (no services in messages)
│   ├── service_pb2.py          # Request/Response message classes
│   └── service_pb2_grpc.py     # gRPC client stubs and server servicers
└── README.md                    # Compilation instructions
```

### Limitations

Proto generation has some limitations compared to REST clients:

- **File uploads**: Multipart/form-data is converted to `bytes` fields (streaming not auto-generated)
- **Authentication**: Must be implemented via gRPC interceptors (not auto-generated)
- **Error codes**: Uses gRPC status codes instead of HTTP status codes
- **No hooks/fetchers**: Proto clients require manual integration (no SWR hooks equivalent)
- **Compilation step**: Proto files must be compiled with `protoc` before use

### When to Use gRPC vs REST

**Use gRPC/Proto when:**
- ✅ You need high performance and low latency
- ✅ Building microservices that communicate internally
- ✅ Need bi-directional streaming
- ✅ Working with polyglot services (multiple languages)
- ✅ Binary efficiency is important

**Use REST when:**
- ✅ Building web/mobile applications with HTTP clients
- ✅ Need browser compatibility without extra tooling
- ✅ Want simpler debugging with HTTP tools
- ✅ Working with third-party integrations
- ✅ Need standard HTTP features (caching, CDN, etc.)

## Type Safety

### TypeScript Types

All request and response types are automatically generated:

```typescript
// Types are inferred automatically
const ticket = await api.getTicket({ id: '123' });
// ticket.id: string
// ticket.title: string
// ticket.description: string
// ticket.priority: 'low' | 'medium' | 'high' | 'critical'
// ticket.status: 'open' | 'in_progress' | 'resolved' | 'closed'
// ticket.created_at: string

// TypeScript will catch errors
const newTicket = await api.createTicket({
  title: 'Test',
  description: 'Test ticket',
  priority: 'invalid'  // ❌ Type error: not assignable
});
```

### Python Types

Generated Python clients use `attrs` classes for type safety:

```python
from cfg_support.models import Ticket, TicketCreate

# Type hints work in IDEs
def process_ticket(ticket: Ticket) -> None:
    print(ticket.id)        # ✓ Valid
    print(ticket.title)     # ✓ Valid
    print(ticket.invalid)   # ❌ IDE error

# Pydantic-style validation
new_ticket = TicketCreate(
    title="Test",
    description="Test ticket",
    priority="high"
)
# Invalid data raises validation error
invalid = TicketCreate(priority="invalid")  # ❌ ValidationError
```

## Best Practices

### 1. Centralize Client Configuration

Create a client factory:

```typescript
// api/client.ts
import SupportAPI from './cfg_support';
import AccountsAPI from './cfg_accounts';

export class APIClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  get support() {
    const client = new SupportAPI(this.baseUrl);
    if (this.token) client.setToken(this.token);
    return client;
  }

  get accounts() {
    const client = new AccountsAPI(this.baseUrl);
    if (this.token) client.setToken(this.token);
    return client;
  }
}

// Usage
const api = new APIClient(process.env.API_URL);
api.setToken(localStorage.getItem('token'));
const tickets = await api.support.listTickets();
```

### 2. Handle Token Refresh

```typescript
class AuthenticatedAPI {
  private api: API;
  private refreshToken: string | null = null;

  constructor(baseUrl: string) {
    this.api = new API(baseUrl);
  }

  async call<T>(fn: () => Promise<T>): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      if (error.response?.status === 401 && this.refreshToken) {
        // Refresh token and retry
        await this.refresh();
        return await fn();
      }
      throw error;
    }
  }

  async refresh() {
    const newToken = await this.api.refreshToken({
      refresh: this.refreshToken
    });
    this.api.setToken(newToken.access);
  }
}
```

### 3. Environment-Specific Configuration

```typescript
// config.ts
const API_URLS = {
  development: 'http://localhost:8000',
  staging: 'https://staging.api.example.com',
  production: 'https://api.example.com'
};

export const getApiUrl = () => {
  const env = process.env.NODE_ENV || 'development';
  return API_URLS[env];
};

// Usage
const api = new API(getApiUrl());
```

### 4. Retry Logic

```python
import backoff
from httpx import HTTPStatusError

@backoff.on_exception(
    backoff.expo,
    HTTPStatusError,
    max_tries=3,
    giveup=lambda e: e.response.status_code < 500
)
def fetch_tickets(client):
    """Fetch tickets with retry logic"""
    return list_tickets.sync(client=client)
```

## Next Steps

- [**Overview**](./overview.md) - Learn about Django-CFG API Client Generation
- [**CLI Usage**](./cli-usage.md) - Generate updated clients
- [**Zone Configuration**](./groups.md) - Configure custom zones

:::tip Regenerate After API Changes
After modifying your Django REST Framework API, regenerate clients to get updated types:
```bash
python manage.py generate --clean
```
:::
