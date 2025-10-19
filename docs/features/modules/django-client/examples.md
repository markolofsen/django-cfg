---
title: Examples
sidebar_position: 3
keywords:
  - django client examples
  - openapi client examples
  - typescript api examples
  - python api examples
description: Real-world examples of using generated API clients. CRUD operations, pagination, file uploads, and advanced patterns.
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Real-World Examples

Practical examples of using generated API clients in production applications.

---

## CRUD Operations

### Create

<Tabs>
  <TabItem value="typescript" label="TypeScript" default>

```typescript
import { createUser } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'
import { UserRequest } from '@/api/generated/cfg__accounts/models'

async function handleCreateUser(formData: UserRequest) {
  try {
    const user = await createUser(formData)
    console.log('Created:', user.id)
    return user
  } catch (error) {
    console.error('Failed to create user:', error)
    throw error
  }
}
```

  </TabItem>
  <TabItem value="python" label="Python">

```python
from api_client import APIClient
from api_client.models import UserRequest

async def create_user(client: APIClient, username: str, email: str):
    try:
        user = await client.accounts.create(data=UserRequest(
            username=username,
            email=email,
            password="secret123"
        ))
        print(f"Created: {user.id}")
        return user
    except Exception as error:
        print(f"Failed to create user: {error}")
        raise
```

  </TabItem>
</Tabs>

### Read (List)

<Tabs>
  <TabItem value="typescript" label="TypeScript" default>

```typescript
import { getUsers } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'

async function loadUsers(page: number = 1) {
  const users = await getUsers({
    page,
    page_size: 20,
    ordering: '-created_at'  // Latest first
  })

  console.log(`Total: ${users.count}`)
  console.log(`Page ${page}: ${users.results.length} users`)

  return users
}
```

  </TabItem>
  <TabItem value="python" label="Python">

```python
async def load_users(client: APIClient, page: int = 1):
    users = await client.accounts.list(
        page=page,
        page_size=20,
        ordering='-created_at'
    )

    print(f"Total: {users.count}")
    print(f"Page {page}: {len(users.results)} users")

    return users
```

  </TabItem>
</Tabs>

### Read (Detail)

<Tabs>
  <TabItem value="typescript" label="TypeScript" default>

```typescript
import { getUserById } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'

async function loadUserProfile(userId: string) {
  try {
    const user = await getUserById(userId)
    return user
  } catch (error) {
    if (error.status === 404) {
      console.error('User not found')
    }
    throw error
  }
}
```

  </TabItem>
  <TabItem value="python" label="Python">

```python
from httpx import HTTPStatusError

async def load_user_profile(client: APIClient, user_id: str):
    try:
        user = await client.accounts.retrieve(id=user_id)
        return user
    except HTTPStatusError as error:
        if error.response.status_code == 404:
            print("User not found")
        raise
```

  </TabItem>
</Tabs>

### Update

<Tabs>
  <TabItem value="typescript" label="TypeScript" default>

```typescript
import { updateUser } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'

async function handleUpdateUser(userId: string, updates: Partial<UserRequest>) {
  const user = await updateUser(userId, updates)
  console.log('Updated:', user.email)
  return user
}
```

  </TabItem>
  <TabItem value="python" label="Python">

```python
async def update_user(client: APIClient, user_id: str, email: str):
    user = await client.accounts.partial_update(
        id=user_id,
        data={"email": email}
    )
    print(f"Updated: {user.email}")
    return user
```

  </TabItem>
</Tabs>

### Delete

<Tabs>
  <TabItem value="typescript" label="TypeScript" default>

```typescript
import { deleteUser } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'

async function handleDeleteUser(userId: string) {
  await deleteUser(userId)
  console.log('Deleted:', userId)
}
```

  </TabItem>
  <TabItem value="python" label="Python">

```python
async def delete_user(client: APIClient, user_id: str):
    await client.accounts.destroy(id=user_id)
    print(f"Deleted: {user_id}")
```

  </TabItem>
</Tabs>

---

## Pagination

### Basic Pagination (React)

```typescript
'use client'
import { useUsers } from '@/api/generated/cfg__accounts/_utils/hooks/accounts'
import { useState } from 'react'

export function UsersPaginated() {
  const [page, setPage] = useState(1)
  const { data, isLoading } = useUsers({ page, page_size: 20 })

  if (isLoading) return <Spinner />

  return (
    <div>
      <UsersList users={data.results} />

      <Pagination
        current={page}
        total={data.count}
        pageSize={20}
        onChange={setPage}
        hasNext={!!data.next}
        hasPrevious={!!data.previous}
      />
    </div>
  )
}
```

### Infinite Scroll (React)

```typescript
'use client'
import { getUsers } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'
import useSWRInfinite from 'swr/infinite'

export function UsersInfiniteScroll() {
  const getKey = (pageIndex: number, previousPageData: any) => {
    // Reached the end
    if (previousPageData && !previousPageData.next) return null

    // First page
    if (pageIndex === 0) return ['users', { page: 1 }]

    // Next pages
    return ['users', { page: pageIndex + 1 }]
  }

  const { data, size, setSize, isLoading } = useSWRInfinite(
    getKey,
    ([_, params]) => getUsers(params)
  )

  const users = data ? data.flatMap(page => page.results) : []
  const hasMore = data && data[data.length - 1]?.next

  return (
    <div>
      {users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}

      {hasMore && (
        <button onClick={() => setSize(size + 1)}>
          Load More
        </button>
      )}
    </div>
  )
}
```

---

## File Uploads

### Single File Upload

```typescript
import { uploadDocument } from '@/api/generated/cfg__documents/_utils/fetchers/documents'

async function handleFileUpload(file: File) {
  const formData = {
    title: file.name,
    description: 'Uploaded file',
    file: file,  // ✅ Type-safe: File | Blob
    is_public: false
  }

  const document = await uploadDocument(formData)
  console.log('Uploaded:', document.id)
  return document
}

// React component
function FileUploadForm() {
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const fileInput = e.currentTarget.querySelector<HTMLInputElement>('input[type="file"]')
    const file = fileInput?.files?.[0]

    if (file) {
      await handleFileUpload(file)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" required />
      <button type="submit">Upload</button>
    </form>
  )
}
```

### Multiple File Upload

```typescript
async function handleMultipleFileUpload(files: File[]) {
  const uploads = files.map(file =>
    uploadDocument({
      title: file.name,
      file: file,
      is_public: true
    })
  )

  const documents = await Promise.all(uploads)
  console.log(`Uploaded ${documents.length} files`)
  return documents
}
```

---

## Search and Filtering

### Search with Debounce

```typescript
'use client'
import { useUsers } from '@/api/generated/cfg__accounts/_utils/hooks/accounts'
import { useState, useEffect } from 'react'
import { useDebouncedValue } from '@/hooks/useDebouncedValue'

export function UsersSearch() {
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebouncedValue(search, 300)

  const { data, isLoading } = useUsers({
    search: debouncedSearch,
    page: 1,
    page_size: 20
  })

  return (
    <div>
      <input
        type="search"
        placeholder="Search users..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {isLoading ? (
        <Spinner />
      ) : (
        <UsersList users={data.results} />
      )}
    </div>
  )
}
```

### Multi-Filter

```typescript
'use client'
import { useUsers } from '@/api/generated/cfg__accounts/_utils/hooks/accounts'
import { useState } from 'react'

export function UsersFiltered() {
  const [filters, setFilters] = useState({
    status: 'active',
    role: '',
    ordering: '-created_at'
  })

  const { data } = useUsers({
    ...filters,
    page: 1,
    page_size: 20
  })

  return (
    <div>
      <select
        value={filters.status}
        onChange={(e) => setFilters({ ...filters, status: e.target.value })}
      >
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>

      <select
        value={filters.role}
        onChange={(e) => setFilters({ ...filters, role: e.target.value })}
      >
        <option value="">All Roles</option>
        <option value="admin">Admin</option>
        <option value="user">User</option>
      </select>

      <UsersList users={data.results} />
    </div>
  )
}
```

---

## Optimistic Updates

### Optimistic Delete

```typescript
'use client'
import { useUsers } from '@/api/generated/cfg__accounts/_utils/hooks/accounts'
import { deleteUser } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'

export function UsersListOptimistic() {
  const { data, mutate } = useUsers({ page: 1 })

  const handleDelete = async (userId: string) => {
    // Optimistic update
    mutate(
      {
        ...data,
        results: data.results.filter(u => u.id !== userId),
        count: data.count - 1
      },
      false  // Don't revalidate yet
    )

    try {
      await deleteUser(userId)
      // Revalidate to ensure consistency
      mutate()
    } catch (error) {
      // Revert on error
      mutate()
      alert('Failed to delete user')
    }
  }

  return (
    <ul>
      {data?.results.map(user => (
        <li key={user.id}>
          {user.username}
          <button onClick={() => handleDelete(user.id)}>Delete</button>
        </li>
      ))}
    </ul>
  )
}
```

### Optimistic Update

```typescript
const handleUpdate = async (userId: string, newEmail: string) => {
  // Optimistic update
  mutate(
    {
      ...data,
      results: data.results.map(u =>
        u.id === userId ? { ...u, email: newEmail } : u
      )
    },
    false
  )

  try {
    await updateUser(userId, { email: newEmail })
    mutate()
  } catch (error) {
    mutate()
    alert('Failed to update user')
  }
}
```

---

## Form Handling

### React Hook Form Integration

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { UserRequestSchema } from '@/api/generated/cfg__accounts/_utils/schemas/UserRequest.schema'
import { createUser } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'
import type { UserRequest } from '@/api/generated/cfg__accounts/models'

export function UserForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<UserRequest>({
    resolver: zodResolver(UserRequestSchema)  // ✅ Zod validation
  })

  const onSubmit = async (data: UserRequest) => {
    try {
      const user = await createUser(data)
      console.log('Created:', user)
    } catch (error) {
      console.error('Failed:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('username')} placeholder="Username" />
      {errors.username && <span>{errors.username.message}</span>}

      <input {...register('email')} type="email" placeholder="Email" />
      {errors.email && <span>{errors.email.message}</span>}

      <input {...register('password')} type="password" placeholder="Password" />
      {errors.password && <span>{errors.password.message}</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Create User'}
      </button>
    </form>
  )
}
```

---

## Error Handling

### TypeScript

```typescript
import { getUsers } from '@/api/generated/cfg__accounts/_utils/fetchers/accounts'

async function fetchUsers() {
  try {
    const users = await getUsers({ page: 1 })
    return { data: users, error: null }
  } catch (error) {
    if (error instanceof Response) {
      const status = error.status
      if (status === 401) {
        // Redirect to login
        window.location.href = '/login'
      } else if (status === 403) {
        return { data: null, error: 'Access denied' }
      } else if (status === 404) {
        return { data: null, error: 'Not found' }
      } else if (status >= 500) {
        return { data: null, error: 'Server error' }
      }
    }

    return { data: null, error: 'Network error' }
  }
}
```

### Python

```python
from httpx import HTTPStatusError

async def fetch_users(client: APIClient):
    try:
        users = await client.accounts.list(page=1)
        return {"data": users, "error": None}
    except HTTPStatusError as error:
        status = error.response.status_code
        if status == 401:
            return {"data": None, "error": "Unauthorized"}
        elif status == 403:
            return {"data": None, "error": "Access denied"}
        elif status == 404:
            return {"data": None, "error": "Not found"}
        elif status >= 500:
            return {"data": None, "error": "Server error"}
    except Exception as error:
        return {"data": None, "error": f"Network error: {str(error)}"}
```

---

## Authentication

### TypeScript (Bearer Token)

```typescript
import { configureAPI } from '@/api/generated/api-instance'

// Configure once on app startup
configureAPI({
  baseUrl: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  getAuthToken: () => {
    // Get token from localStorage, cookies, etc.
    return localStorage.getItem('auth_token')
  },
})
```

### Python (Bearer Token)

```python
from api_client import APIClient

def get_auth_token():
    # Get token from env, session, etc.
    return os.getenv('AUTH_TOKEN')

client = APIClient(
    base_url="https://api.example.com",
    headers={
        "Authorization": f"Bearer {get_auth_token()}"
    }
)
```

---

## Custom Actions

Django ViewSet custom actions are automatically available:

```python
# Django ViewSet
class UserViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active users"""
        ...

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Reset user password"""
        ...
```

**Generated TypeScript:**

```typescript
// List action (detail=False)
const activeUsers = await client.users.active()

// Detail action (detail=True)
await client.users.resetPassword(userId, {
  new_password: 'secret123'
})
```

**Generated Python:**

```python
# List action
active_users = await client.users.active()

# Detail action
await client.users.reset_password(
    id=user_id,
    data={"new_password": "secret123"}
)
```

---

## Next Steps

- **[Advanced Topics](./advanced)** - Groups, CI/CD, archiving
- **[Troubleshooting](./troubleshooting)** - Common issues and solutions
- **[Overview](./overview)** - Feature overview
