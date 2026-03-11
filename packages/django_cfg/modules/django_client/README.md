# django_client

A multi-language API client generator for Django REST Framework.

Parses your OpenAPI schema and produces type-safe client code in **Python**, **TypeScript**, **Go**, **Swift**, and **Protocol Buffers** — all from a single intermediate representation.

---

## Overview

```
OpenAPI spec (3.0.3 / 3.1.0 / 3.1.x)
         │
         ▼
    parse_openapi()
         │
         ▼
      IRContext  ◄─── single source of truth
         │
    ┌────┴─────────────────────────────────┐
    ▼        ▼        ▼        ▼           ▼
Python   TypeScript  Go     Swift    Protocol Buffers
(httpx)  (Fetch+Zod) (net/http) (URLSession) (gRPC)
```

The IR (Intermediate Representation) is a language-agnostic model that all parsers write to and all generators read from. This means parser logic and generator logic are completely independent.

---

## Architecture

```
django_client/
├── core/
│   ├── ir/                   # Intermediate Representation models
│   │   ├── context.py        # IRContext (root), OpenAPIInfo, DjangoGlobalMetadata
│   │   ├── schema.py         # IRSchemaObject — one schema component
│   │   └── operation.py      # IROperationObject, IRParameterObject, IRRequest/ResponseObject
│   ├── parser/               # OpenAPI → IR converters
│   │   ├── openapi30.py      # OpenAPI 3.0.x parser
│   │   └── openapi_modern.py # OpenAPI 3.1.x parser
│   ├── generator/            # IR → code generators
│   │   ├── python/           # Python (Pydantic 2 + httpx, async)
│   │   ├── typescript/       # TypeScript (Fetch API + Zod schemas)
│   │   ├── go/               # Go (net/http, context-aware)
│   │   ├── proto/            # Protocol Buffers (gRPC service definitions)
│   │   └── swift_codable/    # Swift (URLSession + Codable)
│   ├── types/                # Unified type system
│   │   ├── field_types.py    # FieldType, FormatType, TypeMapper
│   │   └── content_type.py   # ContentType enum
│   ├── detection/            # Smart field semantics detection
│   │   └── field_detector.py # detect_field_meta() — infers InputType from field names
│   ├── context/              # Pre-computed template contexts
│   │   ├── field_context.py  # FieldContext, SchemaContext, build_*_context()
│   │   └── params_builder.py # OperationParamsContext, ParamsBuilder
│   └── utils/                # Shared utilities
│       ├── naming.py         # Case conversion helpers
│       ├── schema_resolver.py # $ref resolver (BFS, circular-safe)
│       └── enum_collector.py  # Enum deduplication
├── generate_client/          # Orchestration layer
│   ├── config.py             # GenerationConfig, LanguageOptions
│   └── orchestrator.py       # ClientGenerationOrchestrator
├── management/commands/      # Django management command
│   └── generate_client.py    # python manage.py generate_client
└── spectacular/              # drf-spectacular customizations
    ├── enum_naming.py        # x-enum-varnames support
    └── async_detection.py    # Async view detection
```

---

## Key Concepts

### Intermediate Representation

The IR is the core of the module. All generation logic is expressed in terms of IR objects.

**IRContext** — root model passed to every generator:

```python
@dataclass
class IRContext:
    openapi_info: OpenAPIInfo          # spec title, version, servers
    django_metadata: DjangoGlobalMetadata  # CSRF, session, split-request settings
    schemas: dict[str, IRSchemaObject] # all schema components
    operations: dict[str, IROperationObject]  # all API operations
```

**IRSchemaObject** — one schema (e.g. `User`, `UserRequest`, `PatchedUser`):

```python
schema.name              # "User"
schema.type              # "object" | "string" | "integer" | ...
schema.properties        # dict[str, IRSchemaObject]
schema.is_request_model  # True for UserRequest
schema.is_patch_model    # True for PatchedUser
schema.related_response  # "User" (points back to response model)
schema.python_type       # computed: "str", "int", "float", ...
schema.typescript_type   # computed: "string", "number", ...
schema.has_enum          # True if enum values are present
```

**IROperationObject** — one API endpoint:

```python
op.operation_id           # "users_list"
op.http_method            # "GET"
op.path                   # "/api/users/"
op.tags                   # ["users"]
op.parameters             # list[IRParameterObject]
op.request_body           # IRRequestBodyObject | None
op.responses              # dict[int, IRResponseObject]
op.is_list_operation      # True for list endpoints
op.path_parameters        # filtered list of path params
```

### Request/Response Split

Django REST Framework with `SPECTACULAR_SETTINGS["COMPONENT_SPLIT_REQUEST"] = True` produces separate schemas for reads and writes:

| Schema | Direction | Example |
|--------|-----------|---------|
| `User` | response (read) | Has `id`, `created_at` |
| `UserRequest` | request (write) | No `id`, no `created_at` |
| `PatchedUserRequest` | PATCH request | All fields optional |

The IR tracks this via `is_request_model`, `is_response_model`, `is_patch_model`, and `related_response`/`related_request` cross-references. All generators handle this split correctly.

### TypeMapper

A single class maps FieldType + FormatType to each target language:

```python
mapper = TypeMapper()

mapper.to_python(FieldType.STRING, FormatType.DATETIME)     # "datetime.datetime"
mapper.to_typescript(FieldType.STRING, FormatType.UUID)     # "string"
mapper.to_go(FieldType.STRING, FormatType.DATETIME)         # "time.Time"
mapper.to_proto(FieldType.INTEGER, FormatType.INT64)        # "int64"
mapper.to_swift(FieldType.BOOLEAN)                          # "Bool"
```

---

## Usage

### Parse an OpenAPI spec

```python
from django_cfg.modules.django_client.core import parse_openapi

with open("openapi.json") as f:
    spec = json.load(f)

ctx = parse_openapi(spec)
print(ctx.schemas.keys())     # all schema names
print(ctx.operations.keys())  # all operation IDs
```

### Generate a client

```python
from django_cfg.modules.django_client.core.generator.python import PythonGenerator
from django_cfg.modules.django_client.core.generator.typescript import TypeScriptGenerator
from django_cfg.modules.django_client.core.generator.go import GoGenerator

files = PythonGenerator(ctx).generate()
for f in files:
    print(f.path)
    print(f.content)
```

### Django management command

```bash
# Generate all enabled languages
python manage.py generate_client

# Generate specific language
python manage.py generate_client --language typescript

# Dry run (print files without writing)
python manage.py generate_client --dry-run
```

### Via orchestrator

```python
from django_cfg.modules.django_client.generate_client import (
    ClientGenerationOrchestrator,
    GenerationConfig,
)
from django_cfg.modules.django_client import get_openapi_service

service = get_openapi_service()
config = GenerationConfig(output_dir="./generated", languages=["python", "typescript"])
orchestrator = ClientGenerationOrchestrator(service, config)
result = orchestrator.generate()
```

---

## Generated Output

### Python

```python
# Generated: models.py
class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

# Generated: client.py
async def users_list(client: httpx.AsyncClient) -> list[User]: ...
async def users_create(client: httpx.AsyncClient, body: UserRequest) -> User: ...
async def users_retrieve(client: httpx.AsyncClient, id: int) -> User: ...
```

### TypeScript

```typescript
// Generated: models.ts
export interface User {
  id: number;
  name: string;
  email: string;
}

// Generated: schemas.ts (Zod)
export const UserSchema = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string().email(),
});

// Generated: client.ts
export async function usersList(): Promise<User[]> { ... }
export async function usersCreate(body: UserRequest): Promise<User> { ... }
```

### Go

```go
// Generated: models.go
type User struct {
    ID        int64  `json:"id"`
    Name      string `json:"name"`
    Email     string `json:"email"`
}

// Generated: client.go
func (c *Client) UsersList(ctx context.Context) ([]User, error) { ... }
func (c *Client) UsersCreate(ctx context.Context, body UserRequest) (*User, error) { ... }
```

### Protocol Buffers

```protobuf
// Generated: users.proto
message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
}

service UsersService {
  rpc UsersList (UsersListRequest) returns (UsersListResponse);
  rpc UsersCreate (UserRequest) returns (User);
}
```

### Swift

```swift
// Generated: Models.swift
struct User: Codable {
    let id: Int
    let name: String
    let email: String
}

// Generated: Client.swift
func usersList() async throws -> [User] { ... }
func usersCreate(body: UserRequest) async throws -> User { ... }
```

---

## Smart Field Detection

The `detect_field_meta()` function infers semantic information from field names:

```python
from django_cfg.modules.django_client.core.detection import detect_field_meta

meta = detect_field_meta("email", FieldType.STRING)
# FieldMeta(input_type=InputType.EMAIL, validation=FieldValidationHint.EMAIL, sensitive=False)

meta = detect_field_meta("password", FieldType.STRING)
# FieldMeta(input_type=InputType.PASSWORD, sensitive=True)

meta = detect_field_meta("description", FieldType.STRING)
# FieldMeta(input_type=InputType.TEXTAREA)
```

This is used by the Python generator to emit HTML form hints and by TypeScript hooks for form validation.

---

## Configuration

Settings are controlled via `DjangoGlobalMetadata` in the IR, which is populated from `SPECTACULAR_SETTINGS` during parsing:

| Setting | Default | Description |
|---------|---------|-------------|
| `COMPONENT_SPLIT_REQUEST` | required | Must be `True`. Enforces separate request/response schemas. |
| `COMPONENT_SPLIT_PATCH` | `True` | Generate `Patched*` schemas for PATCH. |
| `csrf_cookie_name` | `"csrftoken"` | Cookie name for CSRF token. |
| `csrf_header_name` | `"X-CSRFToken"` | Header name for CSRF. |
| `session_cookie_name` | `"sessionid"` | Session cookie name. |

---

## Testing

```bash
# Run all tests
cd projects/django-cfg
PYTHONPATH=src python -m pytest src/django_cfg/modules/django_client/tests/ -q

# Run unit tests only
PYTHONPATH=src python -m pytest src/django_cfg/modules/django_client/tests/unit/ -q

# Run by language
PYTHONPATH=src python -m pytest -m go
PYTHONPATH=src python -m pytest -m typescript
PYTHONPATH=src python -m pytest -m swift

# Run integration tests
PYTHONPATH=src python -m pytest src/django_cfg/modules/django_client/tests/integration/ -v
```

Tests use a DSL from `tests/fixtures/` for constructing IR objects:

```python
from django_cfg.modules.django_client.tests.fixtures import (
    make_schema, make_field, make_operation, make_context,
)

ctx = make_context(
    schemas={"User": make_schema("User", properties={"name": make_field("name", "string")})},
    operations={"users_list": make_operation("users_list", "GET", "/api/users/")},
)
files = PythonGenerator(ctx).generate()
```

---

## Adding a New Language

1. Create `core/generator/<language>/` package
2. Implement `<Language>Generator(BaseGenerator)` with a `generate() -> list[GeneratedFile]` method
3. Add type mappings to `TypeMapper` in `core/types/field_types.py`
4. Add language option to `GenerationConfig` in `generate_client/config.py`
5. Register in `generate_client/generators/internal.py`
6. Write tests in `tests/unit/generator/test_<language>_v2.py`
