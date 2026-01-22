"""
Encryption configuration models for Django-CFG.

This module provides Pydantic configuration models for optional API encryption,
allowing field-level or response-level encryption of sensitive data.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class EncryptionLevel(str, Enum):
    """Encryption level options."""

    NONE = "none"
    FIELD = "field"  # Encrypt specific fields only
    RESPONSE = "response"  # Encrypt entire response


class EncryptionAlgorithm(str, Enum):
    """Supported encryption algorithms."""

    AES_256_GCM = "AES-256-GCM"
    AES_256_CBC = "AES-256-CBC"


class KeyDerivationConfig(BaseModel):
    """Key derivation function configuration."""

    algorithm: Literal["PBKDF2", "scrypt"] = Field(
        default="PBKDF2",
        description="Key derivation algorithm",
    )
    iterations: int = Field(
        default=100_000,
        ge=10_000,
        le=1_000_000,
        description="Number of iterations for PBKDF2",
    )
    salt_length: int = Field(
        default=16,
        ge=8,
        le=32,
        description="Salt length in bytes",
    )
    hash_function: Literal["SHA-256", "SHA-512"] = Field(
        default="SHA-256",
        description="Hash function for key derivation",
    )


class KeyRotationConfig(BaseModel):
    """Automatic key rotation configuration."""

    enabled: bool = Field(
        default=False,
        description="Enable automatic key rotation",
    )
    interval_days: int = Field(
        default=90,
        ge=1,
        le=365,
        description="Days between key rotations",
    )
    retain_previous: int = Field(
        default=2,
        ge=0,
        le=10,
        description="Number of previous keys to retain for decryption",
    )


class FieldEncryptionConfig(BaseModel):
    """Field-level encryption configuration."""

    enabled: bool = Field(
        default=True,
        description="Enable field-level encryption",
    )
    default_fields: list[str] = Field(
        default_factory=list,
        description="Fields to encrypt by default across all serializers",
    )
    exclude_fields: list[str] = Field(
        default_factory=list,
        description="Fields to never encrypt",
    )


class ResponseEncryptionConfig(BaseModel):
    """Response-level encryption configuration."""

    enabled: bool = Field(
        default=False,
        description="Enable full response encryption",
    )
    content_type: str = Field(
        default="application/json+encrypted",
        description="Content-Type for encrypted responses",
    )
    header_name: str = Field(
        default="X-Encrypt-Response",
        description="Request header to trigger encryption",
    )
    query_param: str = Field(
        default="encrypt",
        description="Query parameter to trigger encryption",
    )


class EncryptionConfig(BaseModel):
    """
    Main encryption configuration for Django-CFG.

    This configuration enables optional API encryption to prevent
    automated data scraping while maintaining seamless UX for legitimate users.

    Example:
        ```python
        from django_cfg import DjangoConfig
        from django_cfg.core.encryption.config import EncryptionConfig

        config = DjangoConfig(
            project_name="myproject",
            encryption=EncryptionConfig(
                enabled=True,
                level="field",
            ),
        )
        ```
    """

    # Master switch
    enabled: bool = Field(
        default=False,
        description="Enable API encryption features",
    )

    # Optional per-request
    optional: bool = Field(
        default=True,
        description="Allow clients to enable/disable encryption per-request",
    )

    # Encryption level
    level: EncryptionLevel = Field(
        default=EncryptionLevel.FIELD,
        description="Default encryption level",
    )

    # Algorithm selection
    algorithm: EncryptionAlgorithm = Field(
        default=EncryptionAlgorithm.AES_256_GCM,
        description="Encryption algorithm to use",
    )

    # Key derivation
    key_derivation: KeyDerivationConfig = Field(
        default_factory=KeyDerivationConfig,
        description="Key derivation configuration",
    )

    # Key rotation
    key_rotation: KeyRotationConfig = Field(
        default_factory=KeyRotationConfig,
        description="Key rotation configuration",
    )

    # Field-level encryption
    field_encryption: FieldEncryptionConfig = Field(
        default_factory=FieldEncryptionConfig,
        description="Field-level encryption settings",
    )

    # Response-level encryption
    response_encryption: ResponseEncryptionConfig = Field(
        default_factory=ResponseEncryptionConfig,
        description="Response-level encryption settings",
    )

    # Per-endpoint overrides (pattern -> level)
    endpoint_overrides: dict[str, EncryptionLevel] = Field(
        default_factory=dict,
        description="Override encryption level per endpoint pattern (regex)",
    )

    # Debug/development options
    expose_algorithm: bool = Field(
        default=True,
        description="Include algorithm name in encrypted response",
    )
    expose_metadata: bool = Field(
        default=True,
        description="Include IV and salt in encrypted response for client decryption",
    )
    log_errors: bool = Field(
        default=True,
        description="Log encryption/decryption errors",
    )

    model_config = {"use_enum_values": True}
