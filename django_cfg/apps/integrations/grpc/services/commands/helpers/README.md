# Command Helpers - Reduce Boilerplate

Command helpers eliminate 70% of repetitive code in gRPC command implementations.

## Quick Start

```python
from django_cfg.apps.integrations.grpc.services.commands.helpers import (
    CommandBuilder,
    command,
    command_with_timestamps,
)

@command_with_timestamps(
    success_status=Bot.Status.RUNNING,
    timestamp_field='started_at',
    log_emoji="▶️"
)
async def start_bot(client, bot) -> bool:
    """Send START command to bot."""
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.start.CopyFrom(pb2.StartCommand())
    return await client._send_command(command)
```

## Components

### 1. CommandBuilder

Auto-generates command metadata (UUID + timestamp).

**Before:**
```python
command = pb2.DjangoCommand(
    command_id=str(uuid.uuid4()),
    timestamp=ProtobufConverter.datetime_to_timestamp(timezone.now())
)
```

**After:**
```python
command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
```

### 2. @command Decorator

Handles:
- Error handling (try/except)
- Logging (entry/success/warning/error)
- Model status updates
- Field updates with asave()

**Parameters:**
- `success_status`: Status to set on model if command succeeds
- `error_status`: Status to set on error (optional)
- `log_emoji`: Emoji for entry log (default: "🔄")
- `update_fields`: Fields to update (default: `['status', 'updated_at']`)
- `log_reason`: Log reason parameter if present (default: True)

**Example:**
```python
@command(success_status=Bot.Status.PAUSED, log_emoji="⏸️")
async def pause_bot(client, bot, reason: str = None) -> bool:
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.pause.CopyFrom(pb2.PauseCommand(reason=reason or ""))
    return await client._send_command(command)
```

### 3. @command_with_timestamps

Variant that also updates timestamp field (started_at, stopped_at, etc).

**Parameters:**
- `success_status`: Status to set on success
- `timestamp_field`: Field to update with current time
- `log_emoji`: Emoji for logging

**Example:**
```python
@command_with_timestamps(
    success_status=Bot.Status.STOPPED,
    timestamp_field='stopped_at',
    log_emoji="⏹️"
)
async def stop_bot(client, bot, reason: str = None) -> bool:
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.stop.CopyFrom(pb2.StopCommand(reason=reason or ""))
    return await client._send_command(command)
```

### 4. Protocols (Type Safety)

Type-safe protocols for model operations:

```python
from django_cfg.apps.integrations.grpc.services.commands.helpers import (
    HasStatus,
    HasConfig,
    HasTimestamps,
)

async def start_bot(client, bot: HasStatus) -> bool:
    # Type checker knows bot has 'status' and 'asave'
    bot.status = "RUNNING"
    await bot.asave(update_fields=['status'])
```

Available protocols:
- `HasStatus` - Models with status field
- `HasConfig` - Models with config (JSONField)
- `HasTimestamps` - Models with created_at/updated_at
- `HasStatusAndTimestamps` - Combined protocol

## Complete Examples

### START Command
```python
@command_with_timestamps(
    success_status=Bot.Status.RUNNING,
    timestamp_field='started_at',
    log_emoji="▶️"
)
async def start_bot(client, bot) -> bool:
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.start.CopyFrom(pb2.StartCommand())
    return await client._send_command(command)
```

### STOP Command (with reason)
```python
@command_with_timestamps(
    success_status=Bot.Status.STOPPED,
    timestamp_field='stopped_at',
    log_emoji="⏹️"
)
async def stop_bot(client, bot, reason: str = None) -> bool:
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.stop.CopyFrom(
        pb2.StopCommand(
            reason=reason or "",
            graceful=True,
            timeout_seconds=30
        )
    )
    return await client._send_command(command)
```

### PING Command (no model update)
```python
@command(log_emoji="🏓")
async def ping(client) -> bool:
    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.ping.CopyFrom(pb2.PingCommand(sequence=1))
    return await client._send_command(command)
```

### CONFIG UPDATE (with refresh)
```python
@command(log_emoji="🔄")
async def update_config(client, bot, force_reload: bool = False) -> bool:
    await bot.arefresh_from_db()
    config_pb = await ProtobufConverter.async_bot_to_protobuf(bot)

    command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
    command.config_update.CopyFrom(
        pb2.ConfigUpdateCommand(
            config=config_pb,
            version=int(bot.updated_at.timestamp()),
            force_reload=force_reload
        )
    )
    return await client._send_command(command)
```

## Benefits

1. **70% Less Code** - Eliminates ~180 lines of boilerplate
2. **Consistent Logging** - Unified emoji and format across all commands
3. **Error Handling** - try/except in one place
4. **Type Safety** - Protocols for compile-time checks
5. **Maintainability** - Changes in one place instead of 6+ files
6. **Reusability** - Works across different projects

## Migration Guide

### Step 1: Import helpers
```python
from django_cfg.apps.integrations.grpc.services.commands.helpers import (
    CommandBuilder,
    command_with_timestamps,
)
```

### Step 2: Replace command creation
```python
# Before
command = pb2.DjangoCommand(
    command_id=str(uuid.uuid4()),
    timestamp=ProtobufConverter.datetime_to_timestamp(timezone.now())
)

# After
command = CommandBuilder.create(pb2.DjangoCommand, ProtobufConverter)
```

### Step 3: Add decorator
```python
@command_with_timestamps(
    success_status=Bot.Status.RUNNING,
    timestamp_field='started_at',
    log_emoji="▶️"
)
```

### Step 4: Remove boilerplate
Remove:
- try/except blocks
- logger.info/warning/error calls
- bot.status assignments
- bot.asave() calls

Keep only:
- Command creation
- Command field population
- Return statement

## What Gets Automatically Handled

The decorator handles:

✅ Entry logging: `"▶️ Sending START BOT to bot-123 (streaming)"`
✅ Reason logging: `"   Reason: manual restart"`
✅ Success logging: `"✅ START BOT sent to bot-123"`
✅ Warning logging: `"⚠️ bot-123 not connected to streaming service"`
✅ Error logging: `"❌ Error sending START BOT to bot-123: ..."`
✅ Status updates: `bot.status = Bot.Status.RUNNING`
✅ Timestamp updates: `bot.started_at = timezone.now()`
✅ Model save: `await bot.asave(update_fields=[...])`
✅ Exception handling: `try/except with exc_info=True`

## Statistics

| Command    | Before | After | Savings |
|------------|--------|-------|---------|
| start.py   | 51     | 13    | 74%     |
| stop.py    | 61     | 15    | 75%     |
| pause.py   | 39     | 11    | 72%     |
| resume.py  | 36     | 11    | 69%     |
| ping.py    | 25     | 9     | 64%     |
| config.py  | 42     | 15    | 64%     |
| **Total**  | **254**| **74**| **71%** |

**~180 lines of boilerplate eliminated!**
