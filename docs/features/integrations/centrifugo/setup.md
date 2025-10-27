# Setup and Configuration

Complete guide to setting up Centrifugo WebSocket RPC integration in your Django-CFG project.

## Prerequisites

- Django-CFG installed
- Python 3.11+
- Redis server (for Centrifugo broker)
- Centrifugo server (or use Docker)

## Installation

### 1. Enable Centrifugo in Django Configuration

Add Centrifugo configuration to your `config.py`:

```python
# api/config.py
from typing import Optional
from django_cfg import DjangoConfig, DjangoCfgCentrifugoConfig
from .environment import env  # Your environment loader

class MyConfig(DjangoConfig):
    # ... other configuration ...

    centrifugo: Optional[DjangoCfgCentrifugoConfig] = (
        DjangoCfgCentrifugoConfig(
            enabled=env.centrifugo.enabled,

            # Wrapper configuration (Django middleware)
            wrapper_url=env.centrifugo.wrapper_url,
            wrapper_api_key=env.centrifugo.wrapper_api_key,

            # Centrifugo server configuration
            centrifugo_url=env.centrifugo.centrifugo_url,
            centrifugo_api_url=env.centrifugo.centrifugo_api_url,
            centrifugo_api_key=env.centrifugo.centrifugo_api_key,
            centrifugo_token_hmac_secret=env.centrifugo.centrifugo_token_hmac_secret,

            # Timeouts and behavior
            ack_timeout=env.centrifugo.default_ack_timeout,
            log_level=env.centrifugo.log_level,

            # Database logging configuration
            log_all_calls=env.centrifugo.log_all_calls,
            log_only_with_ack=env.centrifugo.log_only_with_ack,
        )
        if env.centrifugo.enabled
        else None
    )
```

### 2. Environment Configuration

Add to your `.env` or YAML environment config:

```yaml
# environment.yaml
centrifugo:
  enabled: true

  # Wrapper (Django middleware)
  wrapper_url: "http://localhost:8001"
  wrapper_api_key: "your-secure-api-key"

  # Centrifugo server
  centrifugo_url: "ws://localhost:8000/connection/websocket"
  centrifugo_api_url: "http://localhost:8000/api"
  centrifugo_api_key: "your-centrifugo-api-key"
  centrifugo_token_hmac_secret: "your-hmac-secret-key"

  # Behavior
  default_ack_timeout: 30  # seconds
  log_level: "INFO"
  log_all_calls: true
  log_only_with_ack: false
```

## Configuration Options

### Required Settings

| Parameter | Type | Description |
|-----------|------|-------------|
| `enabled` | `bool` | Enable/disable Centrifugo integration |
| `wrapper_url` | `str` | URL of Django wrapper service |
| `wrapper_api_key` | `str` | API key for wrapper authentication |
| `centrifugo_url` | `str` | WebSocket URL for Centrifugo |
| `centrifugo_api_url` | `str` | HTTP API URL for Centrifugo |
| `centrifugo_api_key` | `str` | API key for Centrifugo server |
| `centrifugo_token_hmac_secret` | `str` | HMAC secret for JWT tokens |

### Optional Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ack_timeout` | `int` | `30` | RPC call timeout in seconds |
| `log_level` | `str` | `"INFO"` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `log_all_calls` | `bool` | `True` | Log all RPC calls to database |
| `log_only_with_ack` | `bool` | `False` | Only log calls that expect acknowledgment |

## Running Centrifugo Server

### Option 1: Docker (Recommended)

Create `docker-compose.centrifugo.yml`:

```yaml
version: '3.8'

services:
  centrifugo:
    image: centrifugo/centrifugo:v5
    ports:
      - "8000:8000"
    environment:
      CENTRIFUGO_TOKEN_HMAC_SECRET_KEY: "your-hmac-secret-key"
      CENTRIFUGO_API_KEY: "your-centrifugo-api-key"
      CENTRIFUGO_ADMIN_PASSWORD: "admin-password"
      CENTRIFUGO_ADMIN_SECRET: "admin-secret"
    command: centrifugo --config=/centrifugo/config.json
    volumes:
      - ./centrifugo.json:/centrifugo/config.json
```

Create `centrifugo.json`:

```json
{
  "token_hmac_secret_key": "your-hmac-secret-key",
  "api_key": "your-centrifugo-api-key",
  "admin_password": "admin-password",
  "admin_secret": "admin-secret",
  "allowed_origins": ["*"],
  "namespaces": [
    {
      "name": "rpc",
      "publish": true,
      "subscribe": true,
      "presence": false,
      "join_leave": false,
      "history_size": 0,
      "history_ttl": 0
    }
  ]
}
```

Run:
```bash
docker-compose -f docker-compose.centrifugo.yml up -d
```

### Option 2: Local Installation

```bash
# macOS
brew install centrifugal/tap/centrifugo

# Linux
wget https://github.com/centrifugal/centrifugo/releases/download/v5.0.0/centrifugo_5.0.0_linux_amd64.tar.gz
tar -xzf centrifugo_5.0.0_linux_amd64.tar.gz
sudo mv centrifugo /usr/local/bin/

# Run with config
centrifugo --config=centrifugo.json
```

## Verifying Installation

### 1. Check Django Configuration

```python
from django_cfg import get_current_config

config = get_current_config()
print(f"Centrifugo enabled: {config.centrifugo.enabled if config.centrifugo else False}")
```

### 2. Check Centrifugo Server

Visit `http://localhost:8000/` - you should see Centrifugo admin interface.

### 3. Test RPC Handler

Create a test handler:

```python
# core/centrifugo_handlers.py
from pydantic import BaseModel
from django_cfg.apps.centrifugo.decorators import websocket_rpc

class PingParams(BaseModel):
    message: str

class PingResult(BaseModel):
    echo: str

@websocket_rpc("system.ping")
async def ping(conn, params: PingParams) -> PingResult:
    return PingResult(echo=f"Received: {params.message}")
```

Register in `apps.py`:

```python
# core/apps.py
class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        from . import centrifugo_handlers
```

### 4. Generate Clients

```bash
python manage.py generate_centrifugo_clients --output ./opensdk --all
```

You should see:
```
Found 1 RPC methods
  - system.ping: PingParams -> PingResult

✓ Generated Python client
✓ Generated TypeScript client
✓ Generated Go client

Successfully generated 3 client(s)
```

## Production Deployment

### Scaling Centrifugo

For production, use multiple Centrifugo instances behind a load balancer:

```yaml
# docker-compose.prod.yml
services:
  centrifugo-1:
    image: centrifugo/centrifugo:v5
    # ... configuration ...

  centrifugo-2:
    image: centrifugo/centrifugo:v5
    # ... configuration ...

  nginx:
    image: nginx:alpine
    ports:
      - "8000:8000"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Security Best Practices

1. **Use HTTPS/WSS in production**:
   ```python
   centrifugo_url="wss://centrifugo.yourdomain.com/connection/websocket"
   ```

2. **Rotate secrets regularly**:
   - `centrifugo_token_hmac_secret`
   - `centrifugo_api_key`
   - `wrapper_api_key`

3. **Use environment variables** for all secrets:
   ```python
   import os

   centrifugo_api_key=os.getenv("CENTRIFUGO_API_KEY")
   ```

4. **Enable CORS restrictions**:
   ```json
   {
     "allowed_origins": ["https://yourdomain.com"]
   }
   ```

## Monitoring

### Enable Logging

```python
centrifugo: DjangoCfgCentrifugoConfig(
    log_level="INFO",
    log_all_calls=True,
)
```

### View Logs in Admin

Navigate to **Django Admin** → **Centrifugo** → **RPC Logs**

View:
- Method name
- Parameters
- Result
- Duration
- Timestamp
- User

## Troubleshooting

### Connection Refused

**Problem**: `WebSocket connection failed`

**Solution**:
1. Check Centrifugo is running: `curl http://localhost:8000/health`
2. Verify `centrifugo_url` in configuration
3. Check firewall rules

### Authentication Failed

**Problem**: `401 Unauthorized`

**Solution**:
1. Verify `centrifugo_token_hmac_secret` matches in Django and Centrifugo
2. Check JWT token generation
3. Verify `wrapper_api_key` is correct

### RPC Timeout

**Problem**: `RPC call timed out after 30s`

**Solution**:
1. Increase `ack_timeout` in configuration
2. Optimize handler logic
3. Check database/network latency

### Handler Not Found

**Problem**: `Method 'foo.bar' not found`

**Solution**:
1. Verify handler is registered: `python manage.py shell`
   ```python
   from django_cfg.apps.centrifugo.router import get_message_router
   router = get_message_router()
   print(router._handlers.keys())
   ```
2. Check `apps.py` imports handlers in `ready()`
3. Verify `@websocket_rpc` decorator is used

## Next Steps

- **[Backend Guide](./backend-guide.md)** - Create your first RPC handler
- **[Client Generation](./client-generation.md)** - Generate type-safe clients
- **[Architecture](./architecture.md)** - Understand how it works

---

:::tip[Production Checklist]
Before deploying to production:
- ✅ Use HTTPS/WSS for all connections
- ✅ Rotate all secrets
- ✅ Configure CORS properly
- ✅ Enable monitoring and logging
- ✅ Test failover scenarios
- ✅ Set up load balancing
:::
