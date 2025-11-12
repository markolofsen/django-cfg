"""
Type-Safe Protocols for Command Handlers

These protocols allow type-safe operations on Django models without tight coupling.
Any model implementing these attributes/methods will pass type checking.

Benefits:
- Type safety without inheritance
- Decoupling from specific model classes
- IDE autocomplete support
- Runtime type checking with @runtime_checkable

Example:
    from django_cfg.apps.integrations.grpc.services.commands.helpers import HasStatus

    async def start_bot(client, bot: HasStatus) -> bool:
        # Type checker knows bot has 'status' and 'asave'
        bot.status = "RUNNING"
        await bot.asave(update_fields=['status'])
        return True
"""

from typing import Protocol, Optional, runtime_checkable


@runtime_checkable
class HasStatus(Protocol):
    """
    Protocol for models with status field.

    Any Django model with 'status' attribute and 'asave' method satisfies this protocol.

    Example Django model:
        class Bot(models.Model):
            status = models.CharField(max_length=20)

            class Status:
                STOPPED = "stopped"
                RUNNING = "running"

            # Django 5.2+ async save
            async def asave(self, update_fields=None):
                ...

    Usage in commands:
        async def start_bot(client, bot: HasStatus) -> bool:
            bot.status = "RUNNING"
            await bot.asave(update_fields=['status'])
    """
    status: str

    async def asave(self, update_fields: Optional[list[str]] = None) -> None:
        """Django async save method (Django 5.2+)."""
        ...


@runtime_checkable
class HasConfig(Protocol):
    """
    Protocol for models with configuration field.

    Example Django model:
        class Bot(models.Model):
            config = models.JSONField(default=dict)

            async def asave(self, update_fields=None):
                ...

            async def arefresh_from_db(self):
                ...

    Usage in commands:
        async def update_config(client, bot: HasConfig) -> bool:
            bot.config['key'] = 'value'
            await bot.asave(update_fields=['config'])
    """
    config: dict

    async def asave(self, update_fields: Optional[list[str]] = None) -> None:
        """Django async save method."""
        ...

    async def arefresh_from_db(self) -> None:
        """Django async refresh from database."""
        ...


@runtime_checkable
class HasTimestamps(Protocol):
    """
    Protocol for models with timestamp fields (created_at, updated_at).

    Example Django model:
        class Bot(models.Model):
            created_at = models.DateTimeField(auto_now_add=True)
            updated_at = models.DateTimeField(auto_now=True)
            started_at = models.DateTimeField(null=True)
            stopped_at = models.DateTimeField(null=True)

            async def asave(self, update_fields=None):
                ...

    Usage:
        async def start_bot(client, bot: HasTimestamps) -> bool:
            from django.utils import timezone
            bot.started_at = timezone.now()
            await bot.asave(update_fields=['started_at'])
    """
    created_at: 'datetime'
    updated_at: 'datetime'

    async def asave(self, update_fields: Optional[list[str]] = None) -> None:
        """Django async save method."""
        ...


@runtime_checkable
class HasStatusAndTimestamps(HasStatus, HasTimestamps, Protocol):
    """
    Combined protocol for models with both status and timestamps.

    Most command handlers need this combination.

    Example:
        async def start_bot(client, bot: HasStatusAndTimestamps) -> bool:
            bot.status = "RUNNING"
            bot.started_at = timezone.now()
            await bot.asave(update_fields=['status', 'started_at', 'updated_at'])
    """
    pass


__all__ = [
    'HasStatus',
    'HasConfig',
    'HasTimestamps',
    'HasStatusAndTimestamps',
]
