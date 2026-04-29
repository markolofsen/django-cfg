"""Name conversions for ts_extras.

Conventions:
    schema.ts file:    PascalCase preserved from OpenAPI ("FleetCreate" → "FleetCreate.ts")
    schema constant:   "<Name>Schema" — what consumers import (z.infer<typeof FleetSchema>)
    hook function:     useCamelCase — "useFleets" / "useCreateFleet"
    folder name:       kebab-case from tag — "fleet-members" → "fleet-members"
"""

from __future__ import annotations

import re

_FIRST_CAP = re.compile(r"(.)([A-Z][a-z]+)")
_ALL_CAP = re.compile(r"([a-z0-9])([A-Z])")


def schema_filename(schema_name: str) -> str:
    return f"{schema_name}.ts"


def schema_constant(schema_name: str) -> str:
    return f"{schema_name}Schema"


def hook_name(operation_id: str, *, method: str) -> str:
    """Map operationId + method to a hook function name.

    Heuristic:
      GET    list_fleets         → useFleets / useListFleets
      GET    get_fleet           → useGetFleet / useFleet
      POST   create_fleet        → useCreateFleet
      DELETE delete_fleet        → useDeleteFleet
      PATCH  update_fleet        → useUpdateFleet
    Always prefix with `use`. CamelCase the operationId tail.
    """
    del method  # intent is in the verb already inside operation_id
    camel = _to_camel(operation_id)
    if not camel:
        return "useOperation"
    return "use" + camel[0].upper() + camel[1:]


def tag_to_folder(tag: str) -> str:
    """Tag → kebab-case folder name. `tag` already comes kebab-cased from FastAPI."""
    return tag.lower().replace("_", "-")


def _to_camel(snake: str) -> str:
    parts = re.split(r"[_\-\s\.]+", snake.strip())
    if not parts:
        return ""
    head, *rest = parts
    return head.lower() + "".join(p.capitalize() for p in rest)


def snake_to_pascal(s: str) -> str:
    return "".join(p.capitalize() for p in re.split(r"[_\-\s\.]+", s.strip()) if p)


# Borrowed from PEP 8 → snake_case helper, kept around in case operations
# come in as PascalCase from a future codegen tool.
def pascal_to_snake(name: str) -> str:
    s1 = _FIRST_CAP.sub(r"\1_\2", name)
    return _ALL_CAP.sub(r"\1_\2", s1).lower()
