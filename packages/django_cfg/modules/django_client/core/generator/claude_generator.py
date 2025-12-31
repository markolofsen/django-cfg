"""
CLAUDE.md Generator - Generates AI assistant documentation for generated clients.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import GeneratedFile

if TYPE_CHECKING:
    from ..ir import IRContext


class ClaudeGenerator:
    """Generates CLAUDE.md documentation for generated API clients."""

    # Content types that trigger URL method generation
    STREAMING_CONTENT_TYPES = frozenset([
        'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime',
        'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/flac',
        'application/octet-stream',
    ])

    def __init__(self, context: "IRContext", language: str, group_name: str = "", **kwargs):
        self.context = context
        self.language = language
        self.group_name = group_name
        self.options = kwargs

    def generate(self) -> GeneratedFile:
        """Generate CLAUDE.md file."""
        info = self.context.openapi_info
        ops_by_tag = self._group_operations_by_tag()
        total_ops = len(self.context.operations)

        # Build resources section
        resources_lines = []
        for tag, ops in sorted(ops_by_tag.items()):
            resources_lines.append(f"- **{tag}** ({len(ops)} ops)")

        resources_str = "\n".join(resources_lines) if resources_lines else "- No resources"

        # Build operations list if few operations
        ops_section = ""
        if total_ops <= 15:
            ops_section = self._build_operations_section(ops_by_tag)

        # Build regenerate command with group name
        regen_cmd = f"python manage.py generate_client --{self.language}"
        if self.group_name:
            regen_cmd = f"python manage.py generate_client --groups {self.group_name} --{self.language}"

        # Get real usage examples
        usage = self._get_usage_examples(ops_by_tag)

        # Get streaming section (TypeScript only)
        streaming_section = self._build_streaming_section(ops_by_tag)

        # Get language-specific "How It Works" section
        how_it_works = self._build_how_it_works_section()

        content = f"""# {info.title} - {self.language.title()} Client

Auto-generated. **Do not edit manually.**

```bash
{regen_cmd}
```

## Stats

| | |
|---|---|
| Version | {info.version} |
| Operations | {total_ops} |
| Schemas | {len(self.context.schemas)} |

## Resources

{resources_str}
{ops_section}
## Usage

{usage}
{streaming_section}
{how_it_works}
"""
        return GeneratedFile(
            path="CLAUDE.md",
            content=content,
            description="AI assistant documentation",
        )

    def _group_operations_by_tag(self) -> dict[str, list]:
        """Group operations by tag."""
        from collections import defaultdict
        ops_by_tag = defaultdict(list)
        for op in self.context.operations.values():
            tag = op.tags[0] if op.tags else "default"
            ops_by_tag[tag].append(op)
        return dict(ops_by_tag)

    def _build_operations_section(self, ops_by_tag: dict) -> str:
        """Build operations list section."""
        lines = ["\n## Operations\n"]
        for tag, ops in sorted(ops_by_tag.items()):
            lines.append(f"**{tag}:**")
            for op in sorted(ops, key=lambda x: x.operation_id):
                method = op.http_method.upper()
                lines.append(f"- `{method}` {op.path} → `{op.operation_id}`")
            lines.append("")
        return "\n".join(lines)

    def _get_usage_examples(self, ops_by_tag: dict) -> str:
        """Get language-specific usage examples with real resource names."""
        if not ops_by_tag:
            return "No operations available."

        tags = list(ops_by_tag.keys())[:2]

        if self.language == "typescript":
            return self._typescript_usage(tags, ops_by_tag)
        elif self.language == "python":
            return self._python_usage(tags, ops_by_tag)
        elif self.language == "go":
            return self._go_usage(tags)
        elif self.language == "proto":
            return self._proto_usage()
        return ""

    def _to_camel(self, tag: str) -> str:
        """Convert tag to camelCase."""
        parts = tag.lower().replace("-", "_").split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    def _typescript_usage(self, tags: list, ops_by_tag: dict) -> str:
        examples = []
        for tag in tags:
            prop = self._to_camel(tag)
            ops = ops_by_tag.get(tag, [])
            has_list = any("list" in op.operation_id.lower() for op in ops)
            has_retrieve = any("retrieve" in op.operation_id.lower() or "read" in op.operation_id.lower() for op in ops)
            has_create = any("create" in op.operation_id.lower() for op in ops)

            if has_list:
                examples.append(f"await client.{prop}.list();")
            if has_retrieve:
                examples.append(f"await client.{prop}.retrieve({{ id: 1 }});")
            if has_create:
                examples.append(f"await client.{prop}.create({{ ... }});")

        if not examples:
            examples = ["await client.<resource>.list();"]

        hooks_section = ""
        if self.options.get("generate_swr_hooks"):
            tag = tags[0] if tags else "resource"
            pascal = "".join(p.capitalize() for p in tag.replace("-", "_").split("_"))
            hooks_section = f"""

**SWR Hooks:**
```typescript
import {{ use{pascal}List }} from './hooks';
const {{ data, isLoading }} = use{pascal}List();
```"""

        return f"""```typescript
import {{ APIClient }} from './';

const client = new APIClient({{ baseUrl, token }});

{chr(10).join(examples)}
```{hooks_section}"""

    def _python_usage(self, tags: list, ops_by_tag: dict) -> str:
        examples = []
        for tag in tags:
            prop = tag.lower().replace("-", "_")
            ops = ops_by_tag.get(tag, [])
            has_list = any("list" in op.operation_id.lower() for op in ops)
            has_retrieve = any("retrieve" in op.operation_id.lower() for op in ops)

            if has_list:
                examples.append(f"await client.{prop}.list()")
            if has_retrieve:
                examples.append(f"await client.{prop}.retrieve(id=1)")

        if not examples:
            examples = ["await client.<resource>.list()"]

        return f"""```python
from .client import APIClient

client = APIClient(base_url="...", token="...")

{chr(10).join(examples)}
```"""

    def _go_usage(self, tags: list) -> str:
        if not tags:
            return "```go\n// See generated files\n```"

        pascal = "".join(p.capitalize() for p in tags[0].replace("-", "_").split("_"))
        return f"""```go
client := api.NewClient(baseURL, token)

result, _ := client.{pascal}.List(ctx)
item, _ := client.{pascal}.Get(ctx, 1)
```"""

    def _proto_usage(self) -> str:
        return """```protobuf
// Generated: messages.proto, services.proto
// Compile: protoc --go_out=. *.proto
```"""

    def _build_how_it_works_section(self) -> str:
        """Build language-specific 'How It Works' section."""
        grp = self.group_name or "<group>"

        base = """## How It Works

```
DRF ViewSets → drf-spectacular → OpenAPI → IR Parser → Generator → This Client
```
"""
        if self.language == "typescript":
            return base + f"""
**Configuration** (`api/config.py`):
```python
openapi_client = OpenAPIClientConfig(
    enabled=True,
    groups=[OpenAPIGroupConfig(name="{grp}", apps=["..."])],
    generate_zod_schemas=True,  # → schemas.ts
    generate_fetchers=True,     # → fetchers.ts
    generate_swr_hooks=True,    # → hooks.ts
)
```

@see https://djangocfg.com/docs/features/api-generation
"""
        elif self.language == "go":
            return base + f"""
**Regenerate:**
```bash
make go  # or: python manage.py generate_api_go
```

**Import paths** are auto-fixed based on target `go.mod`.

@see https://djangocfg.com/docs/features/api-generation
"""
        elif self.language == "python":
            return base + f"""
**Configuration** (`api/config.py`):
```python
openapi_client = OpenAPIClientConfig(
    enabled=True,
    groups=[OpenAPIGroupConfig(name="{grp}", apps=["..."])],
)
```

@see https://djangocfg.com/docs/features/api-generation
"""
        elif self.language == "proto":
            return base + """
**Compile for Go:**
```bash
protoc --go_out=. --go-grpc_out=. *.proto
```

@see https://djangocfg.com/docs/features/api-generation
"""
        else:
            return base + "\n@see https://djangocfg.com/docs/features/api-generation\n"

    def _is_streaming_operation(self, operation) -> bool:
        """Check if operation returns streaming/binary content."""
        primary_response = operation.primary_success_response
        if primary_response and primary_response.content_type:
            content_type = primary_response.content_type.lower()
            if content_type in self.STREAMING_CONTENT_TYPES:
                return True
            if content_type.startswith('video/') or content_type.startswith('audio/'):
                return True
        return False

    def _get_streaming_operations(self) -> list:
        """Get list of operations that have URL builder methods."""
        streaming_ops = []
        for op in self.context.operations.values():
            if self._is_streaming_operation(op):
                streaming_ops.append(op)
        return streaming_ops

    def _build_streaming_section(self, ops_by_tag: dict) -> str:
        """Build section about streaming URL methods (TypeScript only)."""
        if self.language != "typescript":
            return ""

        streaming_ops = self._get_streaming_operations()
        if not streaming_ops:
            return ""

        # Group by tag
        ops_by_tag_streaming = {}
        for op in streaming_ops:
            tag = op.tags[0] if op.tags else "default"
            if tag not in ops_by_tag_streaming:
                ops_by_tag_streaming[tag] = []
            ops_by_tag_streaming[tag].append(op)

        lines = ["\n## Streaming URL Methods\n"]
        lines.append("For streaming endpoints (video, audio, file downloads), additional `*Url()` methods are generated.")
        lines.append("These return the full URL with JWT token - use them for `<video>`, `<audio>`, or `fetch()` downloads.\n")

        for tag, ops in sorted(ops_by_tag_streaming.items()):
            prop = self._to_camel(tag)
            lines.append(f"**{tag}:**")
            for op in ops:
                op_id = op.operation_id
                # Remove tag prefix for method name
                if op.tags:
                    t = op.tags[0].lower().replace("-", "_").replace(" ", "_")
                    if op_id.lower().startswith(t):
                        op_id = op_id[len(t):].lstrip("_")
                # Convert to camelCase
                parts = op_id.split("_")
                method_name = parts[0].lower() + "".join(p.capitalize() for p in parts[1:])
                lines.append(f"- `client.{prop}.{method_name}Url(...)` → streaming URL with token")
            lines.append("")

        lines.append("```typescript")
        lines.append("// Example: Video streaming")
        lines.append("const url = client.terminalMedia.streamStreamRetrieveUrl(sessionId, filePath);")
        lines.append("<video src={url} controls />")
        lines.append("")
        lines.append("// Example: File download")
        lines.append("const url = client.terminalMedia.streamStreamRetrieveUrl(sessionId, archivePath);")
        lines.append("const response = await fetch(url);")
        lines.append("const blob = await response.blob();")
        lines.append("```")

        return "\n".join(lines)
