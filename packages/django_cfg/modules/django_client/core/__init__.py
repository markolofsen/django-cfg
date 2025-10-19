"""
OpenAPI Client Generator.

Universal, pure Python OpenAPI client generator.
No Django dependencies - can be used standalone or with any framework.
"""

__version__ = "1.0.0"

# Configuration
# Archive
from .archive import ArchiveManager
from .config import (
    DjangoOpenAPI,
    OpenAPIConfig,
    OpenAPIError,
    OpenAPIGroupConfig,
    get_openapi_service,
)

# Generators
from .generator import PythonGenerator, TypeScriptGenerator

# Groups
from .groups import GroupDetector, GroupManager

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
    "OpenAPIConfig",
    "OpenAPIGroupConfig",
    "DjangoOpenAPI",
    "OpenAPIError",
    "get_openapi_service",
    "GroupManager",
    "GroupDetector",
    "ArchiveManager",
    "IRContext",
    "IROperationObject",
    "IRSchemaObject",
    "parse_openapi",
    "OpenAPI30Parser",
    "OpenAPI31Parser",
    "PythonGenerator",
    "TypeScriptGenerator",
]
