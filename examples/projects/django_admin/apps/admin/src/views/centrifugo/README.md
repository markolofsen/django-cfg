# Centrifugo Management View

Real-time monitoring and management interface for Centrifugo.

## Overview

This view provides a comprehensive dashboard for monitoring and managing Centrifugo real-time messaging infrastructure. It replaces the previous Django template-based dashboard with a modern React implementation using Next.js 15.

## Architecture

### Structure

```
views/centrifugo/
├── index.tsx                    # Main view component with tabs
├── events.ts                    # Event definitions and emitters
├── types/
│   └── index.ts                 # Type exports from contexts
├── components/
│   ├── SystemStatus.tsx         # Health check and connection status
│   ├── StatCards.tsx            # Overview statistics cards
│   ├── OverviewTab.tsx          # Charts and ACK statistics
│   ├── PublishesTab.tsx         # Recent publishes with filters
│   ├── ChannelsTab.tsx          # Channel statistics
│   ├── LiveChannelsTab.tsx      # Live channel monitoring
│   ├── TestingTab.tsx           # Testing tools
│   ├── dialogs/
│   │   ├── PublishTestDialog.tsx
│   │   ├── PublishWithLoggingDialog.tsx
│   │   ├── SendAckDialog.tsx
│   │   ├── ChannelHistoryDialog.tsx
│   │   └── ChannelPresenceDialog.tsx
│   └── index.ts                 # Component exports
└── README.md                    # This file
```

### Data Flow

```
Context Providers (from @djangocfg/api)
    ↓
CentrifugoView (with all 3 providers)
    ↓
Tab Components (consume contexts via hooks)
    ↓
Dialogs (event-driven, listen via useEventListener)
```

## Features

### 1. System Status
- Redis connection monitoring
- Centrifugo server health check
- Real-time status updates

### 2. Statistics Cards
- Total publishes count
- Success rate percentage
- Average duration
- Failed/timeout count

### 3. Overview Tab
- Publish timeline chart (24h)
- Success/failure breakdown
- ACK statistics
  - Total ACKs received
  - Average ACKs per publish
  - ACK tracking rate

### 4. Recent Publishes Tab
- Paginated table of recent publishes
- Filters:
  - Channel filter
  - Status filter (success/failed/timeout)
- Pagination controls
- Status badges with color coding

### 5. Channels Tab
- Channel statistics table
- Metrics per channel:
  - Total publishes
  - Success rate
  - Average duration
  - Average ACKs
  - Last activity timestamp
- Quick actions:
  - View channel history
  - View channel presence

### 6. Live Channels Tab
- Real-time channel listing
- Pattern-based search
- Active channel status

### 7. Testing Tools Tab
- Publish test message
- Publish with database logging
- Manual ACK sending
- Usage guide

## Contexts Used

### 1. CentrifugoMonitoringContext
**From:** `@djangocfg/api/cfg/contexts/centrifugo`

**Provides:**
- `health` - Health check data
- `overview` - Overview statistics
- `timeline` - Timeline data for charts
- `publishes` - Recent publishes with pagination
- Refresh methods for each

### 2. CentrifugoAdminApiContext
**From:** `@djangocfg/api/cfg/contexts/centrifugo`

**Provides:**
- `getAuthToken()` - Get auth token for WebSocket
- `listChannels()` - List active channels
- `getChannelHistory()` - Get channel message history
- `getServerInfo()` - Get Centrifugo server info
- `getPresence()` - Get channel presence
- `getPresenceStats()` - Get presence statistics

### 3. CentrifugoTestingContext
**From:** `@djangocfg/api/cfg/contexts/centrifugo`

**Provides:**
- `generateConnectionToken()` - Generate JWT token
- `publishTest()` - Publish test message
- `publishWithLogging()` - Publish with DB logging
- `sendAck()` - Send manual ACK

## Event System

All dialogs are event-driven using the `@djangocfg/ui` event bus.

### Event Flow

1. Component emits event (e.g., `emitOpenPublishTestDialog()`)
2. Dialog listens via `useEventListener()`
3. Dialog opens and handles data
4. Dialog closes and optionally refreshes data

### Available Events

```typescript
CENTRIFUGO_EVENTS = {
  OPEN_PUBLISH_TEST_DIALOG
  OPEN_PUBLISH_WITH_LOGGING_DIALOG
  OPEN_SEND_ACK_DIALOG
  OPEN_CHANNEL_HISTORY_DIALOG
  OPEN_CHANNEL_PRESENCE_DIALOG
  REFRESH_OVERVIEW
  REFRESH_PUBLISHES
  REFRESH_CHANNELS
}
```

## UI Components Used

From `@djangocfg/ui`:

- **Layout:** Card, Tabs, Dialog, Sheet
- **Forms:** Input, Textarea, Select, Switch, Button, Label
- **Data Display:** Table, Badge, Alert, Skeleton
- **Feedback:** Toast (via useToast hook)
- **Icons:** Lucide React icons

## Routing

**Route Definition:** `/src/core/routes/definitions.ts`
```typescript
readonly centrifugo = this.route('/private/centrifugo', {
  label: 'Centrifugo',
  description: 'Real-time messaging and monitoring',
  icon: Radio,
  protected: true,
  group: 'system',
  order: 2,
});
```

**Page File:** `/src/pages/private/centrifugo.tsx`

**URL:** `/private/centrifugo`

**Menu Location:** System group (after Infrastructure)

## API Endpoints Used

All endpoints are from the Django CFG Centrifugo API:

### Monitoring Endpoints
- `GET /api/centrifugo/monitor/health/` - Health check
- `GET /api/centrifugo/monitor/overview/?hours=24` - Overview stats
- `GET /api/centrifugo/monitor/timeline/?hours=24&interval=hour` - Timeline data
- `GET /api/centrifugo/monitor/publishes/?channel=&status=&offset=0&count=50` - Recent publishes
- `GET /api/centrifugo/monitor/channels/?hours=24` - Channel stats

### Admin API Endpoints
- `POST /api/centrifugo/admin-api/server/auth-token/` - Get auth token
- `POST /api/centrifugo/admin-api/server/channels/` - List channels
- `POST /api/centrifugo/admin-api/server/history/` - Get channel history
- `POST /api/centrifugo/admin-api/server/info/` - Get server info
- `POST /api/centrifugo/admin-api/server/presence/` - Get presence
- `POST /api/centrifugo/admin-api/server/presence-stats/` - Get presence stats

### Testing Endpoints
- `POST /api/centrifugo/admin-api/testing/connection-token/` - Generate connection token
- `POST /api/centrifugo/admin-api/testing/publish-test/` - Publish test message
- `POST /api/centrifugo/admin-api/testing/publish-with-logging/` - Publish with logging
- `POST /api/centrifugo/admin-api/testing/send-ack/` - Send ACK

## Django Template Migration

This view replaces the Django template-based dashboard:

**Previous:** `/src/django_cfg/apps/centrifugo/templates/django_cfg_centrifugo/`

**New:** `/src/@frontend/apps/admin/src/views/centrifugo/`

### Key Differences

1. **Framework:** Django templates → React + Next.js
2. **State Management:** jQuery/vanilla JS → React hooks + SWR
3. **UI Components:** Tailwind classes → @djangocfg/ui components
4. **Data Fetching:** Manual fetch → Generated API hooks
5. **Real-time Updates:** Manual polling → SWR automatic revalidation
6. **Type Safety:** None → Full TypeScript types

## Development

### Adding a New Tab

1. Create tab component in `components/`
2. Add to `components/index.ts` exports
3. Import in `index.tsx`
4. Add to Tabs component

### Adding a New Dialog

1. Create dialog component in `components/dialogs/`
2. Add event to `events.ts`
3. Add to `components/dialogs/index.ts` exports
4. Import in main `index.tsx`
5. Render at bottom of view

### Testing

Visit `/private/centrifugo` in your browser after authentication.

The view will automatically:
- Connect to API contexts
- Fetch data on mount
- Refresh data periodically (via SWR)
- Handle loading/error states

## Notes

- All dialogs are rendered at the view level (not within tabs)
- Context providers wrap the entire view
- Loading states use Skeleton components
- Error states display user-friendly messages
- All forms use React Hook Form + Zod validation (if needed)
- Toast notifications for user feedback
