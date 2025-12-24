"""
OpenAPI Client Generator.

Universal, pure Python OpenAPI client generator.
No Django dependencies - can be used standalone or with any framework.

Architecture:
- Config: OpenAPIConfig, DjangoOpenAPI, get_openapi_service
- Groups: GroupManager, GroupDetector
- Parsing: parse_openapi, OpenAPI30Parser, OpenAPI31Parser
- IR: IRContext, IRSchemaObject, IROperationObject
- Generation: Use ClientGenerationOrchestrator from generate_client module

Generators are internal implementation details:
- TypeScript/Python/Go/Proto: generator/ (built-in)
- Swift: external/ (apple/swift-openapi-generator CLI wrapper)
"""

__version__ = "1.0.0"

# Configuration
from .config import (
    DjangoOpenAPI,
    OpenAPIConfig,
    OpenAPIError,
    OpenAPIGroupConfig,
    get_openapi_service,
)

# Groups
from .groups import GroupDetector, GroupManager

# Archiver
from .archiver import ArchiveManager

# IR Models
from .ir import (
    IRContext,
    IROperationObject,
    IRSchemaObject,
)

# Parsers
from .parser import OpenAPI30Parser, OpenAPI31Parser, parse_openapi

__all__ = [
    "__version__",
    # Config
    "OpenAPIConfig",
    "OpenAPIGroupConfig",
    "DjangoOpenAPI",
    "OpenAPIError",
    "get_openapi_service",
    # Groups
    "GroupManager",
    "GroupDetector",
    # Archiver
    "ArchiveManager",
    # IR
    "IRContext",
    "IROperationObject",
    "IRSchemaObject",
    # Parsers
    "parse_openapi",
    "OpenAPI30Parser",
    "OpenAPI31Parser",
]
