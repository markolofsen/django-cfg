---
title: "Django Real-Time Notifications - 4 Patterns with django-ipc"
description: "Send real-time notifications from Django without polling. 4 notification patterns: user, room, broadcast, multi-user. 99.9% request reduction with instant delivery."
sidebar_label: "Real-Time Notifications"
sidebar_position: 5
keywords:
  - django-ipc notifications
  - django real-time notifications
  - websocket notifications django
  - django push notifications
  - websocket notification patterns
  - real-time django messaging
  - django websocket broadcast
schema:
  - type: HowTo
---

import { HowToSchema } from '@site/src/components/Schema';

<HowToSchema
  name="Implement Real-Time Notifications in Django"
  description="4 notification patterns for real-time communication without polling"
  totalTime="PT15M"
  steps={[
    { text: 'Send to specific user', url: '#pattern-1-send-to-specific-user' },
    { text: 'Broadcast to all users', url: '#pattern-2-broadcast-to-all-users' },
    { text: 'Send to room (group messaging)', url: '#pattern-3-send-to-room' },
    { text: 'Send to multiple users', url: '#pattern-4-send-to-multiple-users' }
  ]}
/>

# Real-Time Notifications


**Send instant notifications to users without polling - examples and patterns**


---

## Why Real-Time Notifications?

Traditional polling is wasteful and slow:

| Approach | Requests/Day | Latency | Server Load | Cost |
|----------|-------------|---------|-------------|------|
| **Polling (3s)** | 28,800 | 3-5 seconds | High | $$$$ |
| **Long-Polling (30s)** | 2,880 | 30 seconds | Medium | $$$ |
| **WebSocket (RPC)** | **1** | **Instant** | **Low** | **$** |

**Savings**: 99.9% reduction in requests, instant delivery

---

## Notification Patterns

### Pattern 1: Send to Specific User

Send notification to all devices of a single user:

```python
# Django backend
from django_ipc.client import RPCClient

rpc = RPCClient()

# User gets notification on all their devices
rpc.send_notification(
    user_id="123",
    message="Your order has been shipped!",
    data={
        "order_id": 42,
        "tracking_number": "1Z999AA10123456784",
        "estimated_delivery": "2024-01-15"
    }
)
```

**Frontend receives** (all user's devices):
```typescript
client.on('notification', (notification) => {
    // Arrives on iPhone, iPad, Browser simultaneously
    console.log(notification.message);  // "Your order has been shipped!"

    showToast({
        title: "Order Update",
        message: notification.message,
        data: notification.data
    });
});
```

**Use Cases**:
- 🛒 Order status updates
- 💳 Payment confirmations
- 📧 New message alerts
- 🔔 Activity notifications

---

### Pattern 2: Broadcast to All Users

Send message to every connected user:

```python
# Broadcast system announcement
rpc.broadcast(
    message="System maintenance in 5 minutes",
    data={
        "scheduled_at": "2024-01-01T10:00:00Z",
        "duration_minutes": 30
    }
)
```

**All connected clients receive instantly**:
```typescript
client.on('broadcast', (message) => {
    // Every user sees this
    showBanner({
        type: 'warning',
        message: message.message,
        duration: message.data.duration_minutes
    });
});
```

**Use Cases**:
- 🚨 System maintenance alerts
- 📢 Platform announcements
- 🎉 Special promotions
- ⚠️ Security alerts

---

### Pattern 3: Send to Room/Group

Send to specific rooms or groups:

```python
# Send to chat room members
rpc.send_to_room(
    room="chat_room_42",
    message="New message from John",
    data={
        "user_id": 456,
        "username": "John Doe",
        "message": "Hello everyone!",
        "timestamp": "2024-01-01T10:00:00Z"
    }
)
```

**Room members receive**:
```typescript
client.joinRoom('chat_room_42');

client.on('room_message', (data) => {
    // Only room members get this
    addMessageToChat({
        username: data.username,
        message: data.message,
        timestamp: data.timestamp
    });
});
```

**Use Cases**:
- 💬 Chat rooms
- 🎮 Multiplayer games
- 👥 Team workspaces
- 📊 Shared dashboards

---

### Pattern 4: Send to Multiple Users

Send to list of specific users:

```python
# Notify team members
team_user_ids = ["123", "456", "789"]

rpc.send_to_users(
    user_ids=team_user_ids,
    message="New task assigned to your team",
    data={
        "task_id": 99,
        "task_title": "Review Q4 report",
        "due_date": "2024-01-15"
    }
)
```

**Only specified users receive notification**.

**Use Cases**:
- 👥 Team notifications
- 📋 Task assignments
- 🎯 Targeted campaigns
- 🏢 Department alerts

---

## Real-World Examples

### Example 1: E-Commerce Order Tracking

**Scenario**: Notify customer when order status changes

```python
# models.py
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_ipc.client import RPCClient

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    tracking_number = models.CharField(max_length=100, blank=True)

@receiver(post_save, sender=Order)
def notify_order_status(sender, instance, created, **kwargs):
    """Send real-time notification on order status change"""

    if not created:  # Only on updates
        rpc = RPCClient()

        # ✅ Instant notification to user
        rpc.send_notification(
            user_id=str(instance.user.id),
            message=f"Your order is now {instance.status}",
            data={
                "order_id": instance.id,
                "status": instance.status,
                "tracking": instance.tracking_number,
            }
        )
```

**Frontend** (instant notification):
```typescript
client.on('notification', (data) => {
    if (data.data.order_id) {
        // Update UI immediately
        updateOrderStatus(data.data.order_id, data.data.status);

        // Show toast
        toast.success(data.message);

        // Play sound
        playNotificationSound();
    }
});
```

**Benefits**:
- ✅ Instant updates (no page refresh)
- ✅ Works across all user's devices
- ✅ No polling overhead
- ✅ Better user experience

---

### Example 2: Live Chat Application

**Scenario**: Real-time chat messages

```python
# views.py
from django_ipc.client import RPCClient

def send_chat_message(request):
    """Send chat message to room"""

    room_id = request.POST['room_id']
    message = request.POST['message']
    user = request.user

    # Save to database
    chat_message = ChatMessage.objects.create(
        room_id=room_id,
        user=user,
        message=message
    )

    # ✅ Broadcast to room members instantly
    rpc = RPCClient()
    rpc.send_to_room(
        room=f"chat_{room_id}",
        message="New chat message",
        data={
            "message_id": chat_message.id,
            "user_id": user.id,
            "username": user.username,
            "message": message,
            "timestamp": chat_message.created_at.isoformat()
        }
    )

    return JsonResponse({"status": "sent"})
```

**Frontend** (instant message display):
```typescript
// Join room
await client.joinRoom('chat_42');

// Receive messages
client.on('room_message', (data) => {
    // Instant display
    appendMessage({
        id: data.message_id,
        username: data.username,
        message: data.message,
        timestamp: new Date(data.timestamp)
    });

    // Scroll to bottom
    scrollToBottom();

    // Show notification if in background
    if (document.hidden) {
        new Notification(`${data.username}: ${data.message}`);
    }
});

// Send message
async function sendMessage(text: string) {
    await client.sendChatMessage({
        room_id: 42,
        message: text
    });
}
```

**Benefits**:
- ✅ Sub-second message delivery
- ✅ 98% reduction in API calls
- ✅ Smooth chat experience
- ✅ Works offline/online seamlessly

---

### Example 3: Live Dashboard Updates

**Scenario**: Real-time KPI dashboard

```python
# tasks.py - Background task
from django_ipc.client import RPCClient

def update_dashboard_metrics():
    """Background task runs every 5 seconds"""

    # Calculate metrics
    metrics = {
        "active_users": get_active_users_count(),
        "revenue_today": get_today_revenue(),
        "orders_pending": get_pending_orders_count(),
        "server_load": get_server_load()
    }

    # ✅ Broadcast to all dashboard viewers
    rpc = RPCClient()
    rpc.send_to_room(
        room="dashboard",
        message="Metrics updated",
        data=metrics
    )
```

**Frontend** (live updating dashboard):
```typescript
// Join dashboard room
await client.joinRoom('dashboard');

// Update metrics in real-time
client.on('room_message', (data) => {
    // Update UI components
    updateMetric('active_users', data.active_users);
    updateMetric('revenue_today', data.revenue_today);
    updateMetric('orders_pending', data.orders_pending);
    updateMetric('server_load', data.server_load);

    // Update charts
    updateChart(data);

    // No page refresh needed!
});
```

**Benefits**:
- ✅ Always up-to-date (5s refresh)
- ✅ 90% reduction in API calls
- ✅ Better performance
- ✅ Real-time feel

---

### Example 4: Multiplayer Game Events

**Scenario**: Broadcast player actions

```python
# game/views.py
from django_ipc.client import RPCClient

def player_action(request):
    """Handle player movement/action"""

    game_id = request.POST['game_id']
    player_id = request.user.id
    action = request.POST['action']  # "move", "attack", etc.
    data = json.loads(request.POST['data'])

    # Update game state
    update_game_state(game_id, player_id, action, data)

    # ✅ Broadcast to all players in game
    rpc = RPCClient()
    rpc.send_to_room(
        room=f"game_{game_id}",
        message="Player action",
        data={
            "player_id": player_id,
            "action": action,
            "position": data.get('position'),
            "timestamp": time.time()
        }
    )

    return JsonResponse({"status": "ok"})
```

**Frontend** (60fps game updates):
```typescript
// Join game room
await client.joinRoom('game_123');

// Receive player actions instantly
client.on('room_message', (data) => {
    // Update other player's position
    updatePlayerPosition(data.player_id, data.position);

    // Animate action
    animateAction(data.action);

    // Smooth 60fps gameplay!
});

// Send player action
function movePlayer(x: number, y: number) {
    client.sendPlayerAction({
        game_id: 123,
        action: 'move',
        position: { x, y }
    });
}
```

**Benefits**:
- ✅ Sub-100ms latency
- ✅ Smooth multiplayer experience
- ✅ 60fps capable
- ✅ Scalable to 1000s of players

---

## Performance Metrics

### Latency Comparison

| Method | Average Latency | P99 Latency |
|--------|----------------|-------------|
| **Polling (5s)** | 2.5 seconds | 5 seconds |
| **Long-Polling** | 500ms | 2 seconds |
| **WebSocket RPC** | **5ms** | **20ms** |

**Result**: 500x faster than polling!

---

### Throughput

| Metric | Capacity |
|--------|----------|
| **Notifications/second** | 50,000 |
| **Concurrent Users** | 10,000 (per server) |
| **Broadcast Latency** | `<10ms` |
| **Message Size** | Up to 1MB |

**Scalability**: Linear horizontal scaling

---

## Best Practices

### ✅ DO: Use Notifications for Real-Time Updates

```python
# ✅ GOOD - Real-time notification
rpc.send_notification(
    user_id=user_id,
    message="Payment processed",
    data={"transaction_id": 123}
)
```

---

### ❌ DON'T: Use Notifications for Large Data

```python
# ❌ BAD - Don't send large payloads
rpc.send_notification(
    user_id=user_id,
    message="Here's all your data",
    data={"huge_array": [... 10000 items ...]}  # Too big!
)

# ✅ GOOD - Send notification, fetch data via API
rpc.send_notification(
    user_id=user_id,
    message="New report available",
    data={"report_id": 123}  # Just the ID
)

# Client fetches: GET /api/reports/123
```

---

### ✅ DO: Include Action Data

```python
# ✅ GOOD - Include what user needs
rpc.send_notification(
    user_id=user_id,
    message="New message from John",
    data={
        "message_id": 456,
        "sender_id": 789,
        "sender_name": "John Doe",
        "preview": "Hey, how are you?",
        "url": "/messages/456"
    }
)
```

---

### ✅ DO: Handle Offline Users

```python
# ✅ GOOD - Fallback for offline users
try:
    rpc.send_notification(...)
except UserOfflineError:
    # Send email or push notification
    send_email_notification(user_id)
```

---

## Related Topics

**Implementation:**
- **[Quick Start](./quick-start)** - 5-minute tutorial
- **[Django Integration](./integration)** - Add to your project
- **[Django Signals Integration](./integration#step-4-add-real-time-notifications)** - Automatic notifications

**Patterns & Examples:**
- **[Use Cases](./use-cases)** - 5 production examples
  - E-commerce order notifications
  - Live chat rooms
  - Dashboard metrics
  - Multiplayer lobbies
  - Price alerts

**Understanding the Flow:**
- **[How It Works](./how-it-works)** - Visual message flow diagrams
- **[Architecture](./architecture)** - System design

**Deployment:**
- **[Production Deployment](./deployment)** - Scale to production

---

## Notification Patterns Quick Reference

**Send to One User:**
```python
rpc.send_notification(user_id="123", message="Hello", data={})
```

**Broadcast to All:**
```python
rpc.broadcast(message="System update", data={})
```

**Send to Room:**
```python
rpc.send_to_room(room="chat_1", message="New message", data={})
```

**Send to Multiple Users:**
```python
rpc.send_to_users(user_ids=["1", "2", "3"], message="Team alert", data={})
```

---

## Need Help?

- **[Quick Start Guide](./quick-start)** - Get started in 5 minutes
- **[Integration Guide](./integration)** - Full Django setup
- **[GitHub Issues](https://github.com/markolofsen/django-ipc/issues)** - Ask questions

---

