"""
Universal protobuf conversion utilities with Pydantic v2 configuration.

This module provides a configurable mixin for converting between:
- Python datetime ↔ Protobuf Timestamp
- Python dict ↔ Protobuf Struct
- Protobuf messages ↔ JSON dicts

**Design Principles**:
- 100% Pydantic v2 configuration
- Type-safe conversion methods
- Async support for Django ORM
- Zero business logic (pure conversion utilities)

**Usage Example**:
```python
from django_cfg.modules.django_grpc.utils.converters import (
    ProtobufConverterMixin,
    ConverterConfig,
)

class MyService(ProtobufConverterMixin):
    def __init__(self):
        self.converter_config = ConverterConfig(
            preserving_proto_field_name=True,
            use_integers_for_enums=False,
        )

    async def handle_message(self, message_pb):
        # Protobuf → dict
        data = self.protobuf_to_dict(message_pb)

        # Create timestamp
        ts = self.datetime_to_timestamp(timezone.now())

        # Dict → struct
        struct = self.dict_to_struct({'key': 'value'})
```

Created: 2025-11-07
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict, ParseDict
import google.protobuf as _protobuf_pkg

# K-5: version-guarded MessageToDict wrapper.
# `including_default_value_fields` was removed in protobuf ≥ 6.33; its replacement
# is `always_print_fields_with_no_presence` (available since ≥ 4.x).
# Without this guard any upgrade to protobuf ≥ 6.33 causes a TypeError at runtime.
_PROTO_VERSION = tuple(
    int(x) for x in _protobuf_pkg.__version__.split(".")[:2]
)


def _message_to_dict(message: Message, **kwargs: object) -> dict:
    """Version-guarded wrapper for MessageToDict that handles the
    including_default_value_fields → always_print_fields_with_no_presence rename.

    K-4 — Unknown field behaviour:
    ``MessageToDict`` (and by extension ``protobuf_to_dict``) **silently drops**
    fields that are present in the binary wire format but absent from the local
    ``.proto`` descriptor.  This is intentional proto3 forward-compatibility
    behaviour: a v2 server can send new fields to a v1 client and the v1 client
    simply ignores them.

    Consequences you must be aware of:
    - If a v2 service adds a new field and a v1 caller converts the response
      with ``protobuf_to_dict``, the new field will **not** appear in the dict.
    - This is not an error or a bug — it is by design.  Log a warning or use
      structured versioning (see K-6/K-7) if you need to detect version skew.
    - To inspect unknown fields at the binary level use
      ``message.DESCRIPTOR.GetOptions()`` or ``message.UnknownFields()``
      (available in protobuf ≥ 3.12 with ``--experimental_allow_proto3_optional``).
    """
    if _PROTO_VERSION >= (6, 33):
        # Rename deprecated kwarg; keep unknown kwargs for forward compat
        if "including_default_value_fields" in kwargs:
            value = kwargs.pop("including_default_value_fields")
            kwargs.setdefault("always_print_fields_with_no_presence", value)
    return MessageToDict(message, **kwargs)  # type: ignore[arg-type]


# ============================================================================
# Configuration
# ============================================================================

class ConverterConfig(BaseModel):
    """
    Pydantic configuration for protobuf conversion behavior.

    **Parameters**:
        preserving_proto_field_name: Use proto field names (not camelCase)
        use_integers_for_enums: Use int values for enums (not string names)
        including_default_value_fields: Include fields with default values
        float_precision: Decimal places for float formatting (None = no rounding)

    **Example - Production Config**:
    ```python
    config = ConverterConfig(
        preserving_proto_field_name=True,  # snake_case field names
        use_integers_for_enums=False,      # String enum names
        including_default_value_fields=True,
    )
    ```

    **Example - Development Config**:
    ```python
    config = ConverterConfig(
        preserving_proto_field_name=False,  # camelCase for JSON APIs
        use_integers_for_enums=True,        # Int enums
        including_default_value_fields=False,
    )
    ```
    """

    preserving_proto_field_name: bool = Field(
        default=True,
        description="Use proto field names (snake_case) instead of JSON names (camelCase)",
    )

    use_integers_for_enums: bool = Field(
        default=False,
        description="Use integer values for enums instead of string names",
    )

    including_default_value_fields: bool = Field(
        default=True,
        description="Include fields with default values in output",
    )

    float_precision: Optional[int] = Field(
        default=None,
        ge=0,
        le=15,
        description="Decimal places for float formatting (None = no rounding)",
    )

    model_config = {
        'extra': 'forbid',
        'frozen': True,
    }


# ============================================================================
# Mixin
# ============================================================================

class ProtobufConverterMixin:
    """
    Mixin providing protobuf conversion utilities.

    **Configuration**:
    Classes using this mixin should set `converter_config` attribute:
    ```python
    class MyService(ProtobufConverterMixin):
        def __init__(self):
            self.converter_config = ConverterConfig(
                preserving_proto_field_name=True,
            )
    ```

    If not set, uses default ConverterConfig().

    **Methods**:
    - datetime_to_timestamp: datetime → Timestamp
    - timestamp_to_datetime: Timestamp → datetime
    - dict_to_struct: dict → Struct
    - struct_to_dict: Struct → dict
    - protobuf_to_dict: Message → dict
    - dict_to_protobuf: dict → Message

    **Example Usage**:
    ```python
    class SignalService(ProtobufConverterMixin):
        converter_config = ConverterConfig()

        async def process_message(self, message_pb):
            # Convert to dict for processing
            data = self.protobuf_to_dict(message_pb)

            # Create response timestamp
            ts = self.datetime_to_timestamp(timezone.now())

            # Build response
            response = ResponseMessage(timestamp=ts)
            return response
    ```
    """

    # Class-level default config (can be overridden per instance)
    converter_config: ConverterConfig = ConverterConfig()

    # ------------------------------------------------------------------------
    # Timestamp Conversions
    # ------------------------------------------------------------------------

    def datetime_to_timestamp(self, dt: Optional[datetime]) -> Optional[Timestamp]:
        """
        Convert Python datetime to Protobuf Timestamp.

        Args:
            dt: Python datetime object (timezone-aware recommended)

        Returns:
            Protobuf Timestamp or None if dt is None

        Example:
        ```python
        from django.utils import timezone

        ts = self.datetime_to_timestamp(timezone.now())
        # Timestamp(seconds=1699380000, nanos=123456789)
        ```

        **Timezone Handling**:
        - Naive datetime → assumes UTC
        - Aware datetime → converts to UTC
        """
        if dt is None:
            return None

        ts = Timestamp()
        ts.FromDatetime(dt)
        return ts

    def timestamp_to_datetime(self, ts: Optional[Timestamp]) -> Optional[datetime]:
        """
        Convert Protobuf Timestamp to Python datetime.

        Args:
            ts: Protobuf Timestamp

        Returns:
            Python datetime object (timezone-aware in UTC) or None

        Example:
        ```python
        dt = self.timestamp_to_datetime(message.created_at)
        # datetime(2024, 11, 7, 12, 30, tzinfo=UTC)
        ```
        """
        if ts is None:
            return None

        return ts.ToDatetime()

    # ------------------------------------------------------------------------
    # Struct Conversions
    # ------------------------------------------------------------------------

    def dict_to_struct(self, data: Optional[Dict[str, Any]]) -> Optional[Struct]:
        """
        Convert Python dict to Protobuf Struct.

        Args:
            data: Python dictionary with JSON-compatible values

        Returns:
            Protobuf Struct or None if data is None

        Example:
        ```python
        settings = {
            'exchange': 'binance',
            'pair': 'BTC/USDT',
            'timeframe': '1h',
        }
        struct = self.dict_to_struct(settings)
        # Use in protobuf: message.settings.CopyFrom(struct)
        ```

        **Supported Types**:
        - str, int, float, bool
        - dict (nested)
        - list (of supported types)

        **Unsupported**:
        - bytes
        - datetime (convert to ISO string first)
        - custom objects
        """
        if data is None:
            return None

        struct = Struct()
        struct.update(data)
        return struct

    def struct_to_dict(self, struct: Optional[Struct]) -> Optional[Dict[str, Any]]:
        """
        Convert Protobuf Struct to Python dict.

        Args:
            struct: Protobuf Struct

        Returns:
            Python dictionary or None if struct is None

        Example:
        ```python
        data = self.struct_to_dict(message.settings)
        # {'exchange': 'binance', 'pair': 'BTC/USDT', ...}
        ```
        """
        if struct is None:
            return None

        return dict(struct)

    # ------------------------------------------------------------------------
    # Message Conversions
    # ------------------------------------------------------------------------

    def protobuf_to_dict(
        self,
        message: Message,
        custom_config: Optional[ConverterConfig] = None,
    ) -> Dict[str, Any]:
        """
        Convert Protobuf message to JSON-serializable dict.

        Uses MessageToDict with configuration from converter_config.

        Args:
            message: Protobuf message instance
            custom_config: Optional override config (uses self.converter_config if None)

        Returns:
            JSON-serializable dictionary

        Example:
        ```python
        data = self.protobuf_to_dict(heartbeat_message)
        # {
        #   'cpu_usage': 45.2,
        #   'memory_usage': 60.1,
        #   'status': 'RUNNING'  # Enum as string
        # }
        ```

        **Field Naming**:
        - preserving_proto_field_name=True → 'cpu_usage' (snake_case)
        - preserving_proto_field_name=False → 'cpuUsage' (camelCase)

        **Enum Handling**:
        - use_integers_for_enums=False → 'RUNNING' (string name)
        - use_integers_for_enums=True → 2 (integer value)
        """
        config = custom_config or self.converter_config

        # K-5: use version-guarded wrapper — `including_default_value_fields`
        # was removed in protobuf ≥ 6.33; _message_to_dict handles the rename.
        result = _message_to_dict(
            message,
            preserving_proto_field_name=config.preserving_proto_field_name,
            use_integers_for_enums=config.use_integers_for_enums,
            including_default_value_fields=config.including_default_value_fields,
        )

        # Apply float precision if configured
        if config.float_precision is not None:
            result = self._round_floats(result, config.float_precision)

        return result

    def dict_to_protobuf(
        self,
        data: Dict[str, Any],
        message_class: type[Message],
        custom_config: Optional[ConverterConfig] = None,
    ) -> Message:
        """
        Convert dict to Protobuf message.

        Uses ParseDict to populate protobuf message from dict.

        Args:
            data: Dictionary with message data
            message_class: Protobuf message class to instantiate
            custom_config: Optional override config

        Returns:
            Populated protobuf message instance

        Example:
        ```python
        data = {
            'bot_id': 'bot_123',
            'status': 'RUNNING',
            'cpu_usage': 45.2,
        }

        message = self.dict_to_protobuf(data, HeartbeatUpdate)
        # HeartbeatUpdate(bot_id='bot_123', status=RUNNING, cpu_usage=45.2)
        ```

        **Field Name Handling**:
        Automatically handles both snake_case and camelCase field names.
        """
        config = custom_config or self.converter_config

        # Create empty message instance
        message = message_class()

        # Populate from dict
        ParseDict(data, message, ignore_unknown_fields=True)

        return message

    # ------------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------------

    def _round_floats(self, data: Any, precision: int) -> Any:
        """
        Recursively round float values in nested dict/list structures.

        Args:
            data: Data structure to process
            precision: Decimal places

        Returns:
            Data with rounded floats
        """
        if isinstance(data, float):
            return round(data, precision)
        elif isinstance(data, dict):
            return {k: self._round_floats(v, precision) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._round_floats(item, precision) for item in data]
        else:
            return data

    # ------------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------------

    @staticmethod
    def create_timestamp_now() -> Timestamp:
        """
        Create Timestamp for current UTC time.

        Returns:
            Timestamp for now

        Example:
        ```python
        message = ResponseMessage(
            timestamp=self.create_timestamp_now()
        )
        ```
        """
        ts = Timestamp()
        ts.GetCurrentTime()
        return ts

    @staticmethod
    def is_timestamp_valid(ts: Timestamp) -> bool:
        """
        Check if Timestamp is valid (not default/zero).

        Args:
            ts: Timestamp to check

        Returns:
            True if timestamp has non-zero value

        Example:
        ```python
        if self.is_timestamp_valid(message.created_at):
            dt = self.timestamp_to_datetime(message.created_at)
        ```
        """
        return ts.seconds != 0 or ts.nanos != 0

    def merge_dicts_to_struct(self, *dicts: Dict[str, Any]) -> Struct:
        """
        Merge multiple dicts and convert to Struct.

        Later dicts override earlier ones.

        Args:
            *dicts: Variable number of dicts to merge

        Returns:
            Merged Struct

        Example:
        ```python
        defaults = {'timeout': 30, 'retries': 3}
        overrides = {'timeout': 60}

        struct = self.merge_dicts_to_struct(defaults, overrides)
        # Struct with timeout=60, retries=3
        ```
        """
        merged: Dict[str, Any] = {}
        for d in dicts:
            if d:
                merged.update(d)

        # merged is always a dict (never None) so dict_to_struct always returns Struct.
        # The Optional[Struct] return type of dict_to_struct handles the None-input
        # path which cannot occur here.
        result = self.dict_to_struct(merged)
        assert result is not None  # guaranteed: merged is a dict, not None
        return result


# ============================================================================
# Standalone Functions
# ============================================================================

def datetime_to_timestamp(dt: Optional[datetime]) -> Optional[Timestamp]:
    """
    Standalone function: Convert datetime to Timestamp.

    Useful when not using mixin.

    Args:
        dt: Python datetime

    Returns:
        Protobuf Timestamp or None
    """
    if dt is None:
        return None

    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts


def timestamp_to_datetime(ts: Optional[Timestamp]) -> Optional[datetime]:
    """
    Standalone function: Convert Timestamp to datetime.

    Args:
        ts: Protobuf Timestamp

    Returns:
        Python datetime or None
    """
    if ts is None:
        return None

    return ts.ToDatetime()


def dict_to_struct(data: Optional[Dict[str, Any]]) -> Optional[Struct]:
    """
    Standalone function: Convert dict to Struct.

    Args:
        data: Python dictionary

    Returns:
        Protobuf Struct or None
    """
    if data is None:
        return None

    struct = Struct()
    struct.update(data)
    return struct


def struct_to_dict(struct: Optional[Struct]) -> Optional[Dict[str, Any]]:
    """
    Standalone function: Convert Struct to dict.

    Args:
        struct: Protobuf Struct

    Returns:
        Python dictionary or None
    """
    if struct is None:
        return None

    return dict(struct)


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Configuration
    'ConverterConfig',

    # Mixin
    'ProtobufConverterMixin',

    # Standalone functions
    'datetime_to_timestamp',
    'timestamp_to_datetime',
    'dict_to_struct',
    'struct_to_dict',
]
