"""
Protobuf to JSON Transformers.

Utilities for transforming protobuf messages to JSON-serializable dictionaries.
"""

from typing import Any, Dict
from google.protobuf.message import Message
from google.protobuf.json_format import MessageToDict


def transform_protobuf_to_dict(message: Message) -> Dict[str, Any]:
    """
    Transform protobuf message to JSON-serializable dict.

    Uses google.protobuf.json_format.MessageToDict with sensible defaults.

    Args:
        message: Protobuf message instance

    Returns:
        JSON-serializable dictionary

    Example:
        ```python
        from .generated import bot_streaming_service_pb2

        heartbeat = bot_streaming_service_pb2.HeartbeatUpdate(
            cpu_usage=45.2,
            memory_usage=60.1
        )

        data = transform_protobuf_to_dict(heartbeat)
        # {'cpu_usage': 45.2, 'memory_usage': 60.1, ...}
        ```
    """
    return MessageToDict(
        message,
        preserving_proto_field_name=True,
        use_integers_for_enums=False,  # Use string names for enums
    )


def transform_with_enum_mapping(
    message: Message,
    enum_mappings: Dict[str, Dict[int, str]]
) -> Dict[str, Any]:
    """
    Transform protobuf with custom enum value mappings.

    Args:
        message: Protobuf message
        enum_mappings: {field_name: {enum_value: string_name}}

    Returns:
        Dictionary with custom enum names

    Example:
        ```python
        transform_with_enum_mapping(
            heartbeat,
            enum_mappings={
                'status': {
                    0: 'UNSPECIFIED',
                    1: 'STOPPED',
                    2: 'RUNNING',
                    3: 'PAUSED',
                    4: 'ERROR',
                }
            }
        )
        ```
    """
    data = MessageToDict(message, preserving_proto_field_name=True)

    # Apply custom enum mappings
    for field_name, mapping in enum_mappings.items():
        if field_name in data:
            enum_value = data[field_name]
            if isinstance(enum_value, int):
                data[field_name] = mapping.get(enum_value, str(enum_value))

    return data


__all__ = [
    "transform_protobuf_to_dict",
    "transform_with_enum_mapping",
]
