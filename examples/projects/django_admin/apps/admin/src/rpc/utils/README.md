# RPC Utilities

Utility functions for WebSocket RPC client.

## createRPCLogger

Creates a configured ClientLogger instance with smart defaults.

**Defaults:**
- Development: `level: 4` (DEBUG), `logRPCCalls: true`
- Production: `level: 3` (INFO), `logRPCCalls: false`

### Usage

```typescript
import { createRPCLogger } from '@/rpc/utils';

// Use with defaults (auto-detects development mode)
const logger = createRPCLogger();

// Override specific settings
const logger = createRPCLogger({
  level: 5, // TRACE
  logRPCCalls: true
});
```

## getSharedRPCLogger

Gets or creates a singleton logger instance. Useful for sharing the same logger across multiple components.

### Usage

```typescript
import { getSharedRPCLogger } from '@/rpc/utils';

// In Component A
const logger = getSharedRPCLogger();
logger.info('Component A initialized');

// In Component B (gets the same logger instance)
const logger = getSharedRPCLogger();
logger.info('Component B initialized');
```

## resetSharedRPCLogger

Resets the shared logger instance. Useful for testing or when you need to recreate the logger.

### Usage

```typescript
import { resetSharedRPCLogger } from '@/rpc/utils';

// Reset the shared logger
resetSharedRPCLogger();

// Next call to getSharedRPCLogger() will create a new instance
```

## Log Levels

```typescript
0 = SILENT  // No logs
1 = ERROR   // Only errors
2 = WARN    // Warnings and errors
3 = INFO    // Info, warnings, and errors (production default)
4 = DEBUG   // Debug, info, warnings, and errors (development default)
5 = TRACE   // All logs including trace
```

## Examples

### Custom logger in component

```typescript
import { createRPCLogger } from '@/rpc/utils';

function MyComponent() {
  const logger = createRPCLogger({ level: 4 });

  logger.debug('Component mounted');
  logger.info('Data loaded');
  logger.warn('Deprecated feature used');
  logger.error('Failed to fetch data');

  return <div>...</div>;
}
```

### Shared logger across app

```typescript
// utils/logger.ts
import { getSharedRPCLogger } from '@/rpc/utils';

export const appLogger = getSharedRPCLogger();

// ComponentA.tsx
import { appLogger } from '@/utils/logger';

function ComponentA() {
  appLogger.info('ComponentA: initialized');
}

// ComponentB.tsx
import { appLogger } from '@/utils/logger';

function ComponentB() {
  appLogger.info('ComponentB: initialized');
}
```
