"""Resources and prompts beside the tool registry.

An entry's body is static text, a file, or a callable. Entries come from code
(``resource_registry.register``) or from a source (a remote manifest) that is
asked on every listing, so a late-arriving manifest needs no re-registration.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

#: Static text, a file, or ``callable(context) -> str`` (prompts: ``(context, arguments)``).
Body = Union[str, Path, Callable[..., str]]


def visible(entry: Any, profile: Any) -> bool:
    """Whether ``profile`` may see ``entry``: an all-tools profile, or a public entry."""
    return profile is None or profile.serves_all_tools or bool(entry.public)


def _text(body: Body, *args: Any) -> str:
    if isinstance(body, Path):
        return body.read_text(encoding="utf-8")
    if callable(body):
        return body(*args)
    return body


@dataclass
class Resource:
    uri: str
    name: str
    body: Body
    description: str = ""
    mime_type: str = "text/markdown"
    public: bool = False

    def definition(self) -> Dict[str, Any]:
        return {"uri": self.uri, "name": self.name, "description": self.description, "mimeType": self.mime_type}

    def read(self, context: Any) -> str:
        return _text(self.body, context)


@dataclass
class Prompt:
    name: str
    body: Body
    description: str = ""
    #: ``[{"name", "description", "required"}]``
    arguments: List[Dict[str, Any]] = field(default_factory=list)
    public: bool = False

    def definition(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"name": self.name, "description": self.description}
        if self.arguments:
            out["arguments"] = self.arguments
        return out

    def render(self, context: Any, arguments: Dict[str, Any]) -> str:
        if callable(self.body) and not isinstance(self.body, Path):
            return self.body(context, arguments)
        text = _text(self.body)
        for key, value in arguments.items():  # `{name}` placeholders of declared arguments
            text = text.replace("{" + key + "}", str(value))
        return text


class _Registry:
    def __init__(self) -> None:
        self._items: Dict[str, Any] = {}
        self._sources: List[Callable[[], List[Any]]] = []

    def add_source(self, source: Callable[[], List[Any]]) -> None:
        if source not in self._sources:
            self._sources.append(source)

    def remove_source(self, source: Callable[[], List[Any]]) -> None:
        if source in self._sources:
            self._sources.remove(source)

    def unregister(self, key: str) -> None:
        self._items.pop(key, None)

    def _all(self) -> Dict[str, Any]:
        every = dict(self._items)
        for source in self._sources:
            for entry in source():
                every.setdefault(self._key(entry), entry)
        return every

    def visible(self, profile: Any = None) -> List[Any]:
        return [e for e in self._all().values() if visible(e, profile)]

    def get(self, key: str, profile: Any = None) -> Optional[Any]:
        entry = self._all().get(key)
        return entry if entry is not None and visible(entry, profile) else None


class ResourceRegistry(_Registry):
    _key = staticmethod(lambda e: e.uri)

    def register(self, uri: str, name: str, body: Body, **kw: Any) -> Resource:
        self._items[uri] = resource = Resource(uri, name, body, **kw)
        return resource


class PromptRegistry(_Registry):
    _key = staticmethod(lambda e: e.name)

    def register(self, name: str, body: Body, **kw: Any) -> Prompt:
        self._items[name] = prompt = Prompt(name, body, **kw)
        return prompt


resource_registry = ResourceRegistry()
prompt_registry = PromptRegistry()
