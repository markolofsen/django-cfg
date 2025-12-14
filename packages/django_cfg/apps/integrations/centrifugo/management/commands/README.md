# Centrifugo Management Commands

Management commands for testing and debugging Centrifugo integration.

## Available Commands

### `centrifugo_publish`

Publish messages to Centrifugo channels for testing and debugging purposes.

#### Usage

```bash
# Publish simple text message
python manage.py centrifugo_publish --channel "ai_chat:workspace:UUID" --message "Hello!"

# Publish JSON data
python manage.py centrifugo_publish -c "notifications" -d '{"type": "alert", "text": "Test"}'

# Publish to AI chat with proper format
python manage.py centrifugo_publish -c "ai_chat:workspace:UUID" -m "Test message"

# Publish custom JSON
python manage.py centrifugo_publish -c "my:channel" -d '{"foo": "bar"}'
```

#### Arguments

**Required:**
- `--channel, -c` - Centrifugo channel name (e.g., `'ai_chat:workspace:UUID'`)

**Message Content (choose one):**
- `--message, -m` - Simple text message to publish
- `--data, -d` - JSON data to publish (e.g., `'{"type": "test", "text": "Hello"}'`)

**Options:**
- `--direct` - Use direct Centrifugo client (bypass wrapper, default: True)

#### Examples

**1. Simple text message:**
```bash
python manage.py centrifugo_publish \
  -c "notifications:user:123" \
  -m "Your order has been shipped!"
```

**2. AI Chat message:**
```bash
python manage.py centrifugo_publish \
  -c "ai_chat:workspace:12f827f2-93d4-4248-9acb-cbd0dfcb5698" \
  -d '{"type":"message_chunk","message_id":"test-123","chunk":"Hello from CLI!"}'
```

**3. Custom event:**
```bash
python manage.py centrifugo_publish \
  -c "events:dashboard" \
  -d '{"event":"user_login","user_id":456,"timestamp":"2025-12-14T14:00:00Z"}'
```

#### Response

On success, you'll see:
```
✅ Message published successfully!
   Message ID: dbc4149b-8518-43fd-ba69-33fe02e2031f
   Published: True
```

#### Channel Naming Conventions

Use `:` for namespace separation (not `#`):

- ✅ Good: `ai_chat:workspace:UUID`
- ✅ Good: `notifications:user:123`
- ❌ Bad: `ai_chat#workspace#UUID` (interpreted as user-limited channel)

The `#` symbol is reserved for user-limited channels in Centrifugo.

#### Error Handling

**Unknown channel:**
```
CommandError: Centrifugo API error: unknown channel
```
This means no clients are subscribed to this channel. The message is published but has no recipients.

**Invalid JSON:**
```
CommandError: Invalid JSON in --data: Expecting value: line 1 column 1
```
Check your JSON syntax. Use single quotes around the JSON string in bash.

#### Use Cases

- **Testing real-time features** - Verify WebSocket connections receive messages
- **Debugging chat** - Send test messages to AI chat channels
- **Load testing** - Script multiple publishes to test performance
- **Integration testing** - Automate message publishing in test suites
- **Manual testing** - Quick way to trigger frontend updates

---

### `generate_centrifugo_clients`

Generate type-safe client SDKs for Centrifugo WebSocket RPC.

See [Client Generation](../../../../docs/features/integrations/centrifugo/client-generation.mdx) for details.

#### Usage

```bash
# Generate Python client
python manage.py generate_centrifugo_clients --output ./clients --python

# Generate TypeScript client
python manage.py generate_centrifugo_clients -o ./clients --typescript

# Generate all clients
python manage.py generate_centrifugo_clients -o ./clients --all
```

---

## See Also

- [Centrifugo Setup Guide](../../../../docs/features/integrations/centrifugo/setup.mdx)
- [Centrifugo Architecture](../../../../docs/features/integrations/centrifugo/architecture.mdx)
- [Backend Integration Guide](../../../../docs/features/integrations/centrifugo/backend-guide.mdx)
- [Frontend Integration Guide](../../../../docs/features/integrations/centrifugo/frontend-guide.mdx)
