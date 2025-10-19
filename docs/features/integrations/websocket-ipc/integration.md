---
title: Django Integration Guide - django-ipc WebSocket RPC Setup
description: Integrate django-ipc into Django in 30 minutes. Add real-time notifications with Django signals, RPC manager wrapper, zero modifications to existing code. Production-ready integration guide.
sidebar_label: Django Integration
sidebar_position: 3
keywords:
  - django-ipc integration
  - django websocket integration
  - websocket rpc django setup
  - integrate django-ipc
  - django real-time integration
  - django websocket signals
  - rpc manager django
schema:
  - type: HowTo
---

import { HowToSchema } from '@site/src/components/Schema';

<HowToSchema
  name="Integrate django-ipc into Django Project"
  description="Step-by-step guide to add real-time django-ipc to existing Django project without modifying existing code"
  totalTime="PT30M"
  steps={[
    { text: 'Install django-ipc package', url: '#step-1-install-package' },
    { text: 'Create RPC server script', url: '#step-2-create-rpc-server-script' },
    { text: 'Create RPC manager wrapper', url: '#step-3-create-rpc-manager-wrapper' },
    { text: 'Add Django settings configuration', url: '#step-4-configure-django-settings' },
    { text: 'Integrate with Django signals for auto-notifications', url: '#step-4-add-real-time-notifications' },
    { text: 'Test integration with manual notifications', url: '#testing-integration' }
  ]}
/>

# Django Integration Guide


**Integrate django-ipc into your existing Django project - step by step**


---

## Overview

This guide shows how to add real-time django-ipc to an existing Django project **without modifying existing code**.

**What you'll add**:
- WebSocket RPC server (separate process)
- RPC client wrapper in Django
- Real-time notifications from Django signals
- Auto-generated frontend clients

**What stays unchanged**:
- Your existing Django models
- Your existing views and APIs
- Your existing database
- Your existing frontend (just add WebSocket client)

---

## Integration Steps

### Step 1: Install Package

```bash
pip install django-ipc
```

**Add to `requirements.txt`**:
```txt
django-ipc>=1.0.0
```

---

### Step 2: Create RPC Server Script

**Create `rpc_server.py` in project root**:
```python
"""
WebSocket RPC Server
Run separately: python rpc_server.py
"""
import asyncio
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django_ipc.server import WebSocketServer
from django_ipc.server.config import ServerConfig, WSServerConfig, AuthMode

# Configuration
config = ServerConfig(
    server=WSServerConfig(
        host="0.0.0.0",
        port=8765,
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/2"),
        auth_mode=AuthMode.JWT,  # Production: use JWT
        jwt_secret=os.getenv("JWT_SECRET", "your-secret-key"),
    )
)

async def main():
    server = WebSocketServer(config)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

**Environment variables** (`.env`):
```bash
REDIS_URL=redis://localhost:6379/2
JWT_SECRET=your-super-secret-jwt-key-change-in-production
```

---

### Step 3: Create RPC Client Wrapper

**Create `myproject/rpc.py`**:
```python
"""
RPC Client Wrapper
Singleton pattern for reusing client across project
"""
from django.conf import settings
from django_ipc.client import RPCClient

class RPCManager:
    """Singleton RPC client manager"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self) -> RPCClient:
        """Get or create RPC client"""
        if self._client is None:
            self._client = RPCClient(
                redis_url=settings.REDIS_URL,
                timeout=30
            )
        return self._client

    def send_notification(self, user_id: str, message: str, data: dict = None):
        """Send notification to user"""
        return self.client.send_notification(
            user_id=user_id,
            message=message,
            data=data or {}
        )

    def send_to_room(self, room: str, message: str, data: dict = None):
        """Send message to room"""
        return self.client.send_to_room(
            room=room,
            message=message,
            data=data or {}
        )

    def broadcast(self, message: str, data: dict = None):
        """Broadcast to all connected users"""
        return self.client.broadcast(
            message=message,
            data=data or {}
        )

    def send_to_users(self, user_ids: list, message: str, data: dict = None):
        """Send to multiple users"""
        return self.client.send_to_users(
            user_ids=user_ids,
            message=message,
            data=data or {}
        )

# Singleton instance
rpc = RPCManager()
```

**Update `settings.py`**:
```python
# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/2")

# WebSocket RPC configuration
RPC_SERVER_URL = os.getenv("RPC_SERVER_URL", "ws://localhost:8765")
```

---

### Step 4: Add Real-Time Notifications

**Option A: Using Django Signals** (automatic):

**Create/update `myapp/signals.py`**:
```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from myproject.rpc import rpc
from .models import Order, Message

@receiver(post_save, sender=Order)
def notify_order_update(sender, instance, created, **kwargs):
    """Notify user when order is created or updated"""

    # Determine message
    if created:
        message = "Your order has been received!"
        notification_type = "order_created"
    else:
        message = f"Your order status: {instance.get_status_display()}"
        notification_type = "order_updated"

    # Send real-time notification
    try:
        rpc.send_notification(
            user_id=str(instance.user.id),
            message=message,
            data={
                "type": notification_type,
                "order_id": instance.id,
                "status": instance.status,
                "total": float(instance.total),
                "items_count": instance.items.count(),
                "created_at": instance.created_at.isoformat()
            }
        )
    except Exception as e:
        # Log error but don't break order creation
        logger.error(f"Failed to send notification: {e}")

@receiver(post_save, sender=Message)
def notify_new_message(sender, instance, created, **kwargs):
    """Notify user when they receive a message"""

    if created and instance.recipient:
        try:
            rpc.send_notification(
                user_id=str(instance.recipient.id),
                message=f"New message from {instance.sender.username}",
                data={
                    "type": "new_message",
                    "message_id": instance.id,
                    "sender_id": instance.sender.id,
                    "sender_name": instance.sender.username,
                    "preview": instance.text[:100],
                    "timestamp": instance.created_at.isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
```

**Register signals in `myapp/apps.py`**:
```python
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        import myapp.signals  # Register signals
```

**Update `myapp/__init__.py`**:
```python
default_app_config = 'myapp.apps.MyAppConfig'
```

---

**Option B: Manual in Views** (explicit control):

**Update `myapp/views.py`**:
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from myproject.rpc import rpc

@api_view(['POST'])
def create_order(request):
    """Create order and send real-time notification"""

    # Your existing order creation logic
    order = Order.objects.create(
        user=request.user,
        total=request.data['total'],
        # ... other fields
    )

    # Add items
    for item_data in request.data['items']:
        OrderItem.objects.create(
            order=order,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )

    # ✅ Send real-time notification
    rpc.send_notification(
        user_id=str(request.user.id),
        message="Your order has been received!",
        data={
            "type": "order_created",
            "order_id": order.id,
            "total": float(order.total),
            "items_count": order.items.count()
        }
    )

    return Response({
        "order_id": order.id,
        "status": "created"
    })
```

---

### Step 5: Add Room-Based Messaging (Optional)

**For chat rooms, collaborative docs, multiplayer games**:

**Create `myapp/views.py`**:
```python
from myproject.rpc import rpc

@api_view(['POST'])
def send_chat_message(request):
    """Send message to chat room"""

    room_id = request.data['room_id']
    message_text = request.data['message']

    # Save to database
    message = ChatMessage.objects.create(
        room_id=room_id,
        user=request.user,
        text=message_text
    )

    # ✅ Broadcast to all room members
    rpc.send_to_room(
        room=f"chat_{room_id}",
        message="new_message",
        data={
            "message_id": message.id,
            "user_id": request.user.id,
            "username": request.user.username,
            "text": message_text,
            "timestamp": message.created_at.isoformat()
        }
    )

    return Response({"status": "sent"})

@api_view(['POST'])
def join_chat_room(request):
    """User joins chat room"""

    room_id = request.data['room_id']

    # Add user to room in database
    ChatRoomMember.objects.get_or_create(
        room_id=room_id,
        user=request.user
    )

    # Notify room members
    rpc.send_to_room(
        room=f"chat_{room_id}",
        message="user_joined",
        data={
            "user_id": request.user.id,
            "username": request.user.username,
            "timestamp": timezone.now().isoformat()
        }
    )

    return Response({"status": "joined"})
```

---

### Step 6: Generate Frontend Clients

**Generate TypeScript + Python clients**:
```bash
python -m django_ipc.codegen.cli generate-clients \
    --output ./frontend/clients \
    --redis-url redis://localhost:6379/2
```

**Install TypeScript client** (React example):
```bash
cd frontend/clients/typescript
npm install
npm run build
```

---

### Step 7: Integrate Frontend

**React example** (`src/services/websocket.ts`):
```typescript
import { RPCClient } from '../clients/typescript';

class WebSocketService {
    private client: RPCClient;
    private static instance: WebSocketService;

    private constructor() {
        // Get server URL from environment
        const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8765';

        this.client = new RPCClient(wsUrl);

        // Set auth token from localStorage
        const token = localStorage.getItem('auth_token');
        if (token) {
            this.client.setAuthToken(token);
        }

        // Setup event listeners
        this.setupListeners();
    }

    static getInstance(): WebSocketService {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService();
        }
        return WebSocketService.instance;
    }

    private setupListeners() {
        // Notifications
        this.client.on('notification', (data) => {
            this.handleNotification(data);
        });

        // Broadcasts
        this.client.on('broadcast', (data) => {
            this.handleBroadcast(data);
        });

        // Room messages
        this.client.on('room_message', (data) => {
            this.handleRoomMessage(data);
        });

        // Connection events
        this.client.on('connect', () => {
            console.log('✅ WebSocket connected');
        });

        this.client.on('disconnect', () => {
            console.log('❌ WebSocket disconnected');
        });

        this.client.on('error', (error) => {
            console.error('WebSocket error:', error);
        });
    }

    private handleNotification(data: any) {
        // Show toast notification
        toast.info(data.message, {
            position: 'top-right'
        });

        // Update Redux/state based on type
        switch (data.data.type) {
            case 'order_created':
                // Dispatch Redux action
                store.dispatch(orderCreated(data.data));
                break;

            case 'order_updated':
                store.dispatch(orderUpdated(data.data));
                break;

            case 'new_message':
                store.dispatch(messageReceived(data.data));
                break;
        }
    }

    private handleBroadcast(data: any) {
        // Show banner for system announcements
        showBanner({
            type: 'info',
            message: data.message,
            data: data.data
        });
    }

    private handleRoomMessage(data: any) {
        // Handle chat room messages
        if (data.message === 'new_message') {
            store.dispatch(chatMessageReceived(data.data));
        }
    }

    async connect() {
        await this.client.connect();
    }

    async joinRoom(roomId: string) {
        await this.client.joinRoom(roomId);
    }

    async leaveRoom(roomId: string) {
        await this.client.leaveRoom(roomId);
    }

    setAuthToken(token: string) {
        this.client.setAuthToken(token);
        localStorage.setItem('auth_token', token);
    }
}

export default WebSocketService.getInstance();
```

**Use in React component**:
```tsx
import React, { useEffect } from 'react';
import WebSocketService from './services/websocket';

function App() {
    useEffect(() => {
        // Connect to WebSocket on app startup
        WebSocketService.connect();

        // Cleanup on unmount
        return () => {
            // Client auto-reconnects, no need to disconnect
        };
    }, []);

    return (
        <div className="App">
            {/* Your app components */}
        </div>
    );
}

export default App;
```

---

## Project Structure After Integration

```
myproject/
├── manage.py
├── rpc_server.py                    # ✅ New: WebSocket RPC server
├── requirements.txt                 # ✅ Updated: added django-ipc
├── .env                             # ✅ New: environment variables
│
├── myproject/
│   ├── settings.py                  # ✅ Updated: REDIS_URL
│   ├── rpc.py                       # ✅ New: RPC client wrapper
│   └── ...
│
├── myapp/
│   ├── models.py                    # Unchanged
│   ├── views.py                     # ✅ Updated: added RPC notifications
│   ├── signals.py                   # ✅ New: automatic notifications
│   ├── apps.py                      # ✅ Updated: register signals
│   └── ...
│
└── frontend/
    ├── clients/                     # ✅ Generated clients
    │   ├── typescript/              # Auto-generated TS client
    │   └── python/                  # Auto-generated Python client
    │
    └── src/
        └── services/
            └── websocket.ts         # ✅ New: WebSocket service
```

---

## Running the Stack

### Development

**Terminal 1** - WebSocket Server:
```bash
python rpc_server.py
```

**Terminal 2** - Django:
```bash
python manage.py runserver
```

**Terminal 3** - Frontend:
```bash
npm run dev  # or yarn dev
```

**Terminal 4** - Redis:
```bash
redis-server
```

---

### Docker Compose

**Create `docker-compose.yml`**:
```yaml
version: '3.8'

services:
  django:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/2
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/myproject
    depends_on:
      - db
      - redis

  rpc_server:
    build: .
    command: python rpc_server.py
    volumes:
      - .:/app
    ports:
      - "8765:8765"
      - "8766:8766"
    environment:
      - REDIS_URL=redis://redis:6379/2
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=myproject
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Run**:
```bash
docker-compose up
```

---

## Testing the Integration

### Test 1: Send Notification from Django Shell

```python
python manage.py shell

from myproject.rpc import rpc

# Send notification
rpc.send_notification(
    user_id="123",
    message="Test notification from Django shell",
    data={"test": True}
)

# Check frontend - notification should appear!
```

---

### Test 2: Create Order and Check Notification

```python
# In Django shell
from myapp.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Create order (triggers signal)
order = Order.objects.create(
    user=user,
    total=99.99
)

# Frontend should receive notification immediately!
```

---

### Test 3: Room-Based Chat

**Backend** (Django shell):
```python
from myproject.rpc import rpc

rpc.send_to_room(
    room="chat_test",
    message="new_message",
    data={
        "user": "Test User",
        "text": "Hello from Django!"
    }
)
```

**Frontend** (Console):
```javascript
await WebSocketService.joinRoom('chat_test');
// Should receive message immediately
```

---

## Best Practices

### ✅ DO: Use Signals for Automatic Notifications

```python
# ✅ GOOD - Automatic, consistent
@receiver(post_save, sender=Order)
def notify_order_update(sender, instance, created, **kwargs):
    rpc.send_notification(...)
```

---

### ✅ DO: Handle RPC Errors Gracefully

```python
# ✅ GOOD - Don't break order creation if RPC fails
try:
    rpc.send_notification(...)
except Exception as e:
    logger.error(f"RPC notification failed: {e}")
    # Order still created!
```

---

### ✅ DO: Use Type Hints

```python
# ✅ GOOD - Clear types
def send_notification(
    user_id: str,
    message: str,
    data: dict[str, Any]
) -> None:
    rpc.send_notification(user_id, message, data)
```

---

### ❌ DON'T: Block Views Waiting for RPC

```python
# ❌ BAD - Blocks view response
response = rpc.send_notification(...)  # Waits for response

# ✅ GOOD - Fire and forget
try:
    rpc.send_notification(...)
except Exception:
    pass  # Log error but don't wait
```

---

## Related Topics

**Next Steps:**
- **[Production Deployment](./deployment)** - Deploy to production with Docker
- **[Real-Time Notifications](./real-time-notifications)** - 4 notification patterns
- **[Room-Based Messaging](./integration#step-5-add-room-based-messaging-optional)** - Chat rooms and group messaging

**Examples & Patterns:**
- **[Use Cases](./use-cases)** - 5 production examples (e-commerce, chat, dashboards)
- **[Quick Start](./quick-start)** - 5-minute tutorial
- **[Business Value](./business-value)** - ROI calculator

**Understanding the System:**
- **[Architecture Overview](./architecture)** - System design and scaling
- **[How It Works](./how-it-works)** - Visual message flow

---

## Common Integration Patterns

**E-Commerce:**
- **[Order Tracking](./use-cases#use-case-1-e-commerce-order-tracking)** - Real-time order status updates

**SaaS Applications:**
- **[Live Dashboard](./use-cases#use-case-3-live-dashboard-metrics)** - Real-time metrics push
- **[Support Tickets](./use-cases#use-case-1-e-commerce-order-tracking)** - Instant notifications

**Social Platforms:**
- **[Live Chat](./use-cases#use-case-2-live-chat-application)** - Room-based messaging
- **[Notifications](./real-time-notifications)** - User notification patterns

---

## Need Help?

- **[Quick Start Guide](./quick-start)** - Get started in 5 minutes
- **[Production Checklist](./deployment#production-checklist)** - Pre-deployment verification
- **[GitHub Issues](https://github.com/markolofsen/django-ipc/issues)** - Report integration issues

---

