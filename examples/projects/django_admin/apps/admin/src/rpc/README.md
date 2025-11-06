# RPC Client

Auto-generated WebSocket RPC client for Django-CFG + Centrifugo integration.

## Paths Reference

```
$ADMIN      = ../../../                                         (admin app root)
$DJANGO     = ../../../../django                                (django project)
$DJANGO_CFG = ../../../../../../projects/django-cfg-dev/src/django_cfg  (django_cfg package sources)
```

## Regeneration

```bash
cd $ADMIN && make rpc
```

## Source Data

The RPC client is generated from:
- **gRPC Services**: `$DJANGO/apps/crypto/grpc_services`
- **Django Config**: `$DJANGO/api/config.py`

## Generator

- **Command**: `$DJANGO/core/management/commands/generate_rpc.py`
- **Codegen Logic**: `$DJANGO_CFG/apps/integrations/centrifugo/codegen`

## Improving the Generator

The codegen logic can be modified directly in `$DJANGO_CFG/apps/integrations/centrifugo/codegen`.

Since `django_cfg` is auto-linked to Django, changes are immediately available. Just re-run `make rpc` to regenerate the client.

## Structure

```
src/rpc/
├── generated/          # Auto-generated (DO NOT EDIT)
│   ├── client.ts       # RPC method wrappers
│   ├── rpc-client.ts   # Base Centrifugo client
│   └── types.ts        # Type definitions
├── utils/              # Manual utilities
│   ├── context.tsx     # React Context
│   ├── useLogger.ts    # Logger hook
│   └── useSubscription.ts  # Subscription hook
└── index.ts            # Public API
```

## Usage

```tsx
import { useWSRPC } from '@/rpc';

function MyComponent() {
  const { client, isConnected } = useWSRPC();

  // Call RPC method
  const result = await client?.someMethod(params);
}
```
