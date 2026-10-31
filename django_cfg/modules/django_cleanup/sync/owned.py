"""
Declare which files an object owns, in one place.

    register_owned_files(Film, keys=lambda film: [f"films/{film.pk}/"])

A key ending in "/" is a prefix: everything under it goes with the object.
This works for a model the project cannot edit (shared database, third party),
which a mixin cannot. The registration connects the delete signal itself.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Dict, Iterable, List, Optional, Tuple, Type

if TYPE_CHECKING:
    from django.db.models import Model

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OwnedFiles:
    """One declaration: how to get an instance's keys, and where they live."""

    model: Type["Model"]
    keys: Callable[["Model"], Iterable[str]]
    storage: str = "default"
    #: Every live key or prefix of this model, for `storage_orphans`; omit to leave the model out of orphan scans.
    all_keys: Optional[Callable[[], Iterable[str]]] = None
    #: `"queue_only"` writes the row but leaves it to another service; `None` follows `FileCleanupConfig.mode`.
    mode: Optional[str] = None


_REGISTRY: Dict[Type["Model"], List[OwnedFiles]] = {}


def register_owned_files(
    model: Type["Model"],
    keys: Callable[["Model"], Iterable[str]],
    *,
    storage: str = "default",
    all_keys: Optional[Callable[[], Iterable[str]]] = None,
    mode: Optional[str] = None,
) -> OwnedFiles:
    """
    Declare the keys or prefixes `model` instances own in `storage`.

    Registering the same model and storage again replaces the earlier entry.
    Needs `FileCleanupConfig.outbox = True`; without it the registration is
    inert and a warning is logged when an owner is deleted.
    """
    if mode not in (None, "delete", "queue_only"):
        raise ValueError(f"mode must be 'delete' or 'queue_only', got {mode!r}")

    entry = OwnedFiles(model=model, keys=keys, storage=storage, all_keys=all_keys, mode=mode)
    entries = [e for e in _REGISTRY.get(model, []) if e.storage != storage]
    entries.append(entry)
    _REGISTRY[model] = entries

    from ..signals import connect_delete_signal

    connect_delete_signal(model)
    return entry


def owned_for(model: Type["Model"]) -> List[OwnedFiles]:
    """Registrations for `model`."""
    return list(_REGISTRY.get(model, []))


def all_registrations() -> List[OwnedFiles]:
    """Every registration, for the orphan scan."""
    return [entry for entries in _REGISTRY.values() for entry in entries]


def owned_entries(instance: "Model") -> List[Tuple[OwnedFiles, str]]:
    """`(registration, key)` pairs for one instance; empty keys are dropped."""
    pairs: List[Tuple[OwnedFiles, str]] = []
    for entry in owned_for(type(instance)):
        for key in entry.keys(instance) or ():
            if key:
                pairs.append((entry, str(key)))
    return pairs


def clear_registry() -> None:
    """Forget every registration. Tests only."""
    _REGISTRY.clear()
