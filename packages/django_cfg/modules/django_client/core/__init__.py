"""
OpenAPI Client Generator.

Universal, pure Python OpenAPI client generator.
No Django dependencies - can be used standalone or with any framework.
"""

__version__ = "1.0.0"

# Configuration
from .config import (
    OpenAPIConfig,
    OpenAPIGroupConfig,
    DjangoOpenAPI,
    OpenAPIError,
    get_openapi_service,
)

# Groups
from .groups import GroupManager, GroupDetector

# Archive
from .archive import ArchiveManager

# IR Models
from .ir import (
    IRContext,
    IROperationObject,
    IRSchemaObject,
)

# Parsers
from .parser import parse_openapi, OpenAPI30Parser, OpenAPI31Parser

# Generators
from .generator import PythonGenerator, TypeScriptGenerator

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
