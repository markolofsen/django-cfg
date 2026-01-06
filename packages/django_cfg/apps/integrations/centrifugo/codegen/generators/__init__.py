"""
Centrifugo code generators package.

Each generator is in its own submodule:
- swift_thin: Swift client generator
- typescript_thin: TypeScript client generator
- go_thin: Go client generator
- python_thin: Python client generator

Prefix utilities are now in the utils module:
    from ...utils import WS_TYPE_PREFIX, add_prefix_to_type_name
"""
