"""
Django-CFG Encryption Module.

Provides optional API encryption for preventing automated data scraping
while maintaining seamless UX for legitimate users.

Features:
    - Field-level encryption via serializer mixin
    - Response-level encryption via renderer
    - AES-256-GCM authenticated encryption
    - Per-user key isolation
    - Request-based encryption toggle

Quick Start:
    ```python
    # 1. Configure in DjangoConfig
    from django_cfg import DjangoConfig
    from django_cfg.core.encryption import EncryptionConfig

    config = DjangoConfig(
        project_name="myproject",
        encryption=EncryptionConfig(
            enabled=True,
            level="field",
        ),
    )

    # 2. Add mixin to serializers
    from django_cfg.core.encryption import EncryptableSerializerMixin

    class ProductSerializer(EncryptableSerializerMixin, serializers.ModelSerializer):
        encrypted_fields = ['price', 'cost']

        class Meta:
            model = Product
            fields = ['id', 'name', 'price', 'cost']

    # 3. Request with encryption
    GET /api/products/?encrypt=true
    # or
    GET /api/products/
    X-Encrypt-Response: true
    ```

Components:
    - EncryptionConfig: Pydantic configuration model
    - EncryptableSerializerMixin: DRF serializer mixin
    - EncryptedJSONRenderer: Full response encryption
    - EncryptionMiddleware: Request encryption detection
    - AES256GCMCipher: Encryption cipher
    - KeyManager: Key management and caching
"""

from .config import (
    EncryptionAlgorithm,
    EncryptionConfig,
    EncryptionLevel,
    FieldEncryptionConfig,
    KeyDerivationConfig,
    KeyRotationConfig,
    ResponseEncryptionConfig,
)
from .ciphers import (
    AES256GCMCipher,
    AuthenticationError,
    CipherBase,
    DecryptionError,
    EncryptionError,
    EncryptionException,
    EncryptionResult,
    InvalidIVLengthError,
    InvalidKeyLengthError,
    KeyError,
    get_default_cipher,
)
from .keys import (
    KeyManager,
    derive_key_from_components,
    derive_key_pbkdf2,
    generate_salt,
    get_key_manager,
    reset_key_manager,
)
from .middleware import EncryptionMiddleware, encryption_enabled
from .renderers import EncryptedJSONRenderer, OptionalEncryptedJSONRenderer
from .serializers import (
    EncryptableSerializerMixin,
    EncryptedCharField,
    EncryptedDecimalField,
    EncryptedFieldMixin,
    EncryptedFloatField,
    EncryptedIntegerField,
    EncryptedJSONField,
)

__all__ = [
    # Config
    "EncryptionConfig",
    "EncryptionLevel",
    "EncryptionAlgorithm",
    "KeyDerivationConfig",
    "KeyRotationConfig",
    "FieldEncryptionConfig",
    "ResponseEncryptionConfig",
    # Ciphers
    "CipherBase",
    "EncryptionResult",
    "AES256GCMCipher",
    "get_default_cipher",
    # Exceptions
    "EncryptionException",
    "EncryptionError",
    "DecryptionError",
    "KeyError",
    "InvalidKeyLengthError",
    "InvalidIVLengthError",
    "AuthenticationError",
    # Keys
    "KeyManager",
    "get_key_manager",
    "reset_key_manager",
    "derive_key_pbkdf2",
    "derive_key_from_components",
    "generate_salt",
    # Middleware
    "EncryptionMiddleware",
    "encryption_enabled",
    # Renderers
    "EncryptedJSONRenderer",
    "OptionalEncryptedJSONRenderer",
    # Serializers
    "EncryptableSerializerMixin",
    "EncryptedFieldMixin",
    "EncryptedCharField",
    "EncryptedIntegerField",
    "EncryptedFloatField",
    "EncryptedDecimalField",
    "EncryptedJSONField",
]
