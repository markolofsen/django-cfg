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

        # Group name for examples
        grp = self.group_name or "<group>"

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

## How It Works

```
DRF ViewSets → drf-spectacular → OpenAPI → IR Parser → Generator → This Client
```

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

**Copy to Next.js** (if `nextjs_admin` configured):
```python
nextjs_admin = NextJsAdminConfig(
    project_path="../frontend/apps/...",
    api_output_path="app/_lib/api/generated",
)
```

@see https://djangocfg.com/docs/features/api-generation
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
