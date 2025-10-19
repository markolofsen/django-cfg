# Support Layout

Modern support ticket system layout with resizable panels and mobile-optimized interface.

## Features

- ✅ **Desktop**: Resizable split-panel view (ticket list | conversation)
- ✅ **Mobile**: Single-column navigation with back/forward flow
- ✅ **Real-time**: Auto-refresh messages after sending
- ✅ **Event-driven**: Dialog management via custom events
- ✅ **Type-safe**: Full TypeScript support with generated API types
- ✅ **Smart UI**: Unread counters, status badges, relative timestamps

## Architecture

```
SupportLayout
├── SupportLayoutProvider (UI state + events wrapper)
│   └── SupportProvider (API context from @djangocfg/api)
│       └── AccountsProvider (for user.id in ticket creation)
└── Components
    ├── TicketList (scrollable ticket cards)
    ├── MessageList (conversation bubbles)
    ├── MessageInput (with keyboard shortcuts)
    └── CreateTicketDialog (event-driven)
```

## Usage

```tsx
import { SupportLayout } from '@djangocfg/layouts';

export default function SupportPage() {
  return <SupportLayout />;
}
```

## Event-based Dialog Opening

```tsx
import { openCreateTicketDialog } from '@djangocfg/layouts';

function MyComponent() {
  return (
    <Button onClick={openCreateTicketDialog}>
      Create Ticket
    </Button>
  );
}
```

## API Integration

Uses generated SWR hooks from `@djangocfg/api/cfg/contexts`:
- `useSupportContext()` - Tickets CRUD, messages CRUD
- Automatic cache revalidation after mutations
- Type-safe request/response handling

## Mobile Optimization

- Auto-detects screen width (≤768px)
- Single-column navigation when mobile
- Back button to return to ticket list
- Optimized touch targets

## Key Components

### TicketCard
- Status badges with color-coding
- Unread message counters
- Relative timestamps
- Click to select

### MessageList
- Auto-scroll to latest message
- User vs. Admin message styling
- Avatar placeholders
- Timestamp formatting

### MessageInput
- Multi-line support (Shift+Enter)
- Submit on Enter
- Disabled when ticket closed
- Loading states

### CreateTicketDialog
- Subject + initial message
- Zod validation
- Auto-selects created ticket
- Toast notifications

