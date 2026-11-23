"""Type-check gate: a generated TypeScript tree that does not type-check is never published.

Runs in ``orchestrator._run_staged`` on the staged tree that is about to replace
the consumer folder, before the git guard and the swap. A failure discards both
stages, so the consumer folder keeps its previous tree, and the target is
reported failed: ``manage.py gen`` exits non-zero with tsc's diagnostics. The
check itself lives in ``tools/external/tsc.py``.

Opt-out: ``DJANGO_CFG_GEN_SKIP_TYPECHECK=1`` for one run. It exists because the
check resolves imports through the consumer's installed dependencies. A tree
whose shim imports ``@djangocfg/api`` needs that package's built ``dist`` types,
which a fresh checkout does not have yet, and a handwritten runtime in the
middle of a change can break a tree that is itself fine. The skip is printed on
every run that uses it.
"""

from __future__ import annotations

from ..config import GenerationTarget
from ..staging import Stage
from ...tools.external import tsc
from .progress import print_note


def typecheck_staged(target: GenerationTarget, staged: Stage) -> None:
    """Raise ``GeneratorError`` when ``staged`` (bound for ``staged.dst``) does not type-check."""
    if target.lang != "typescript":
        return
    if tsc.is_skipped():
        print_note(target.name, f"type-check skipped ({tsc.SKIP_ENV}=1)")
        return
    tsc.typecheck(staged.path, final=staged.dst)


__all__ = ["typecheck_staged"]
