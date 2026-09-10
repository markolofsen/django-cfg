#!/usr/bin/env python3
"""Keep every django_llm tree synchronized from one source of truth.

    django_cfg.modules.django_llm          ← CANON
      ├─ cmdop_django/modules/django_llm
      ├─ carapis .../modules/django_llm
      ├─ mls .../modules/django_llm
      └─ cmdop_packaging/pypi/cmdop-llm    (DISABLED — a diverged branch)

Usage (from the module root, via ./sync.sh, or directly):

    sync.py check                # read-only; exits 1 on drift
    sync.py sync                 # canon -> every tree
    sync.py promote project      # this tree -> canon -> every tree
    sync.py promote package      # the PyPI tree -> canon -> every tree
    sync.py <cmd> --dry-run      # print what would change, touch nothing

`promote` always routes through the canon, so a change never travels
mirror-to-mirror.

STDLIB ONLY, deliberately. This script repairs trees, so it must run when the
engine beside it is broken — importing the engine would make a broken tree
unrepairable. It also must not import `pytest`, Django, or anything installed
per-checkout.

Replaced `sync_mirrors.sh` on 2026-09-10. The shell version derived its root by
walking seven `..` blind, which resolved to a nonexistent directory when
invoked through a symlinked checkout and reported it as "canonical tree not
found". Roots are now discovered by looking for a marker.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

# ─── CONFIG — the only block to edit when a checkout moves or joins ──────────

#: Where the canon lives, relative to the workspace root.
CANONICAL_REL = "djangocfg/projects/django-cfg/src/django_cfg/modules/django_llm"

#: The PyPI package tree, relative to the workspace root. Its tests sit one
#: level above the engine directory rather than inside it.
PACKAGE_ROOT_REL = "cmdop/projects/solution/cmdop_packaging/pypi/cmdop-llm"


@dataclass(frozen=True)
class Mirror:
    label: str
    rel: str
    flavour: str          # "project" | "package"
    skip_tests: bool = False
    enabled: bool = True
    disabled_because: str = ""


MIRRORS: tuple[Mirror, ...] = (
    Mirror("cmdop", "cmdop/projects/solution/cmdop_django/modules/django_llm", "project"),
    Mirror("carapis", "carapis/solution/projects/django/modules/django_llm", "project"),
    Mirror("mls", "mls/mls-new/projects/django/modules/django_llm", "project"),
    Mirror("figurino", "figurino/web/projects/django/modules/django_llm", "project"),
    Mirror(
        "package",
        f"{PACKAGE_ROOT_REL}/cmdop_llm",
        "package",
        skip_tests=True,
        enabled=False,
        disabled_because=(
            "DIVERGED BRANCH, not a stale mirror (2026-09-09). It trails the canon "
            "in most files while carrying subsystems the canon never had, so a "
            "delete-sync would remove working code rather than refresh it. "
            "`promote package` is the safe direction. See the tree's CLAUDE.md."
        ),
    ),
)

#: Owned by a host, never copied and never deleted. `@dev/` is here because a
#: sync destroyed three authored plans on 2026-09-10 — plans are per-checkout.
#: `@docs/` is deliberately NOT here: it documents the engine, and keeping it
#: per-tree let the canon name `cmdop_server.llm` (a package that exists only
#: under .archive) in 21 files while carapis had quietly fixed all 21.
HOST_OWNED: tuple[str, ...] = (
    "_integration.py",
    "apps.py",
    "management",
    "CLAUDE.md",
    "README.md",
    "@dev",
    "pyproject.toml",
    "py.typed",
)

#: Never carried in either direction.
JUNK: tuple[str, ...] = ("__pycache__", ".cache", ".DS_Store")

# ─── end CONFIG ─────────────────────────────────────────────────────────────

CANONICAL_PKG = "django_cfg.modules.django_llm"
PROJECT_PKG = "modules.django_llm"
PACKAGE_PKG = "cmdop_llm"

#: Import-path rewrites. The canon spells the package one way and each flavour
#: of tree another; the text is otherwise identical, which is what lets one
#: `@docs/` page serve every tree.
#:
#: The lookbehind matters: without it `modules.django_llm` inside an already-
#: qualified `django_cfg.modules.django_llm` matches too, and the canon fills
#: up with `django_cfg.django_cfg.modules...`.
_TO_CANONICAL = (
    (re.compile(rf"(?<!django_cfg\.)\b{re.escape(PROJECT_PKG)}\b"), CANONICAL_PKG),
    (re.compile(rf"\b{re.escape(PACKAGE_PKG)}\b"), CANONICAL_PKG),
)
_TO_PROJECT = ((re.compile(rf"\b{re.escape(CANONICAL_PKG)}\b"), PROJECT_PKG),)
_TO_PACKAGE = ((re.compile(rf"\b{re.escape(CANONICAL_PKG)}\b"), PACKAGE_PKG),)

TRANSFORMS = {
    "canonical": _TO_CANONICAL,
    "project": _TO_PROJECT,
    "package": _TO_PACKAGE,
}


def rewrite(text: str, flavour: str) -> str:
    """Apply one flavour's import-path substitutions."""
    for pattern, replacement in TRANSFORMS[flavour]:
        text = pattern.sub(replacement, text)
    return text


def is_host_owned(rel: Path) -> bool:
    head = rel.parts[0] if rel.parts else ""
    return head in HOST_OWNED or str(rel) in HOST_OWNED


def is_junk(rel: Path) -> bool:
    return any(part in JUNK for part in rel.parts) or rel.suffix == ".pyc"


#: Mirrored, but never rewritten — these files contain the literal spellings
#: the transform searches for, so rewriting them destroys their meaning.
VERBATIM: tuple[str, ...] = (
    # This script. Rewriting it would corrupt the transform itself, and the
    # next sync would spread the damage to every tree.
    ".scripts",
    # The transform's own tests: they assert on both spellings by name, so a
    # rewrite turns `assert canon_form -> project_form` into
    # `assert project_form -> project_form`, which passes while proving nothing.
    "tests/test_sync_script.py",
)


def is_verbatim(rel: Path) -> bool:
    """Whether ``rel`` must be copied byte-for-byte, without rewriting."""
    return (bool(rel.parts) and rel.parts[0] in VERBATIM) or str(rel) in VERBATIM


def walk(root: Path, *, skip_tests: bool = False):
    """Yield engine-owned paths relative to ``root``, in a stable order."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if is_junk(rel) or is_host_owned(rel):
            continue
        if skip_tests and rel.parts and rel.parts[0] == "tests":
            continue
        yield rel


def render(source: Path, rel: Path, flavour: str) -> bytes:
    """The bytes ``rel`` should have in a tree of ``flavour``."""
    raw = (source / rel).read_bytes()
    if is_verbatim(rel):
        return raw
    try:
        return rewrite(raw.decode("utf-8"), flavour).encode("utf-8")
    except UnicodeDecodeError:
        return raw          # binary asset — copy through untouched


@dataclass
class Plan:
    written: list[Path]
    deleted: list[Path]

    @property
    def empty(self) -> bool:
        return not self.written and not self.deleted


def plan_tree(source: Path, target: Path, flavour: str, *, skip_tests: bool = False) -> Plan:
    """What syncing ``source`` into ``target`` would change. Touches nothing."""
    written: list[Path] = []
    wanted: set[Path] = set()

    for rel in walk(source, skip_tests=skip_tests):
        wanted.add(rel)
        desired = render(source, rel, flavour)
        current = target / rel
        if not current.exists() or current.read_bytes() != desired:
            written.append(rel)

    deleted = [
        rel for rel in walk(target, skip_tests=skip_tests)
        if rel not in wanted
    ]
    return Plan(written, sorted(deleted))


def apply_tree(source: Path, target: Path, flavour: str, *, skip_tests: bool = False) -> Plan:
    """Make ``target`` an exact copy of ``source`` in ``flavour`` spelling."""
    plan = plan_tree(source, target, flavour, skip_tests=skip_tests)

    for rel in plan.written:
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(render(source, rel, flavour))
        shutil.copymode(source / rel, destination)

    for rel in plan.deleted:
        (target / rel).unlink(missing_ok=True)

    _prune_empty_dirs(target)
    return plan


def _prune_empty_dirs(root: Path) -> None:
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


#: Where `ENGINE_VERSION` lives, relative to a tree root.
VERSION_FILE = "config.py"
_VERSION_RE = re.compile(r'^ENGINE_VERSION\s*:\s*str\s*=\s*["\']([^"\']+)["\']', re.M)


def read_version(tree: Path) -> tuple[int, ...] | None:
    """``ENGINE_VERSION`` from ``tree``, as a comparable tuple.

    Parsed rather than imported: this script must work against a tree whose
    engine is broken, which is exactly when importing it would fail.

    ``None`` means the file or the constant is absent — a tree predating
    versioning. Treated as "unknown", never as "older", so an unversioned tree
    is reported rather than silently overwritten.
    """
    path = tree / VERSION_FILE
    if not path.is_file():
        return None
    match = _VERSION_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    if not match:
        return None
    try:
        return tuple(int(part) for part in match.group(1).split("."))
    except ValueError:
        return None


def format_version(version: tuple[int, ...] | None) -> str:
    return ".".join(str(p) for p in version) if version else "unversioned"


def check_downgrade(source: Path, target: Path, label: str) -> str | None:
    """Refuse when ``source`` would overwrite a NEWER ``target``.

    The failure this exists for: a checkout that has fallen behind runs `sync`,
    and `--delete` quietly reverts everyone else to its stale state. Returns a
    message to refuse with, or None to proceed.
    """
    ours, theirs = read_version(source), read_version(target)
    if ours is None or theirs is None:
        return None                     # unknown, not older — see read_version
    if theirs > ours:
        return (
            f"REFUSED — {label} is at {format_version(theirs)}, ahead of the "
            f"source's {format_version(ours)}. Syncing would revert it. "
            f"Promote {label} first, or bump the source."
        )
    return None


def find_workspace_root(start: Path) -> Path:
    """Walk up until the canon is visible, and return the directory holding it.

    Resolves symlinks first. The shell version walked a fixed number of levels,
    which broke the moment a checkout was reached through `~/djangocfg`.
    """
    override = os.environ.get("WORKSPACE_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / CANONICAL_REL).is_dir():
            return candidate
    raise SystemExit(
        f"ERROR: no workspace root above {start} contains {CANONICAL_REL}.\n"
        f"       Set WORKSPACE_ROOT to the directory holding the checkouts."
    )


def report(label: str, plan: Plan) -> None:
    for rel in plan.written:
        print(f"{label}: write    {rel}")
    for rel in plan.deleted:
        print(f"{label}: delete   {rel}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="sync.py", description="Synchronize the django_llm trees."
    )
    parser.add_argument("command", choices=("check", "sync", "pull", "promote"))
    parser.add_argument("source", nargs="?", choices=("project", "package"))
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print the plan without writing anything (implied by `check`)",
    )
    args = parser.parse_args(argv)

    here = Path(__file__).resolve().parent.parent      # the module root
    workspace = find_workspace_root(here)
    canon = workspace / CANONICAL_REL
    package_root = workspace / PACKAGE_ROOT_REL

    present, missing, disabled = [], [], []
    for mirror in MIRRORS:
        path = workspace / mirror.rel
        if not mirror.enabled:
            disabled.append(mirror)
        elif path.is_dir():
            present.append((mirror, path))
        else:
            missing.append((mirror, path))

    # This checkout is always synced, whether or not it appears in MIRRORS.
    targets = [(m.label, p, m.flavour, m.skip_tests) for m, p in present]
    if here != canon and not any(p == here for _, p in present):
        targets.insert(0, ("this-checkout", here, "project", False))

    if args.command == "promote":
        if not args.source:
            parser.error("promote needs a source: project | package")
        if args.source == "project":
            origin, flavour, skip = here, "canonical", False
        else:
            origin, flavour, skip = package_root / "cmdop_llm", "canonical", True
            if not origin.is_dir():
                raise SystemExit(f"ERROR: package tree not present at {origin}")
        # A promote overwrites the canon, so this is the direction where a
        # stale tree does the most damage.
        refusal = check_downgrade(origin, canon, "the canon")
        if refusal:
            print(refusal, file=sys.stderr)
            return 1
        if args.dry_run:
            report("canon", plan_tree(origin, canon, flavour, skip_tests=skip))
        else:
            apply_tree(origin, canon, flavour, skip_tests=skip)
            if args.source == "package":
                apply_tree(package_root / "tests", canon / "tests", "canonical")

    drift = False
    refused = False
    inspecting = args.command == "check" or args.dry_run
    for label, path, flavour, skip in targets:
        # A tree ahead of the canon is a promote waiting to happen, not drift
        # to flatten. Report it and leave the tree alone.
        refusal = check_downgrade(canon, path, label)
        if refusal:
            print(refusal, file=sys.stderr)
            refused = True
            continue
        plan = (plan_tree if inspecting else apply_tree)(canon, path, flavour, skip_tests=skip)
        if not plan.empty:
            drift = True
            if inspecting:
                report(label, plan)

    # Name what was NOT checked. A silently skipped tree reads as "in sync",
    # which is the one conclusion this script must never imply.
    for mirror, path in missing:
        print(f"SKIPPED — {mirror.label} not present at {path}", file=sys.stderr)
    for mirror in disabled:
        print(f"SKIPPED — {mirror.label}: {mirror.disabled_because}", file=sys.stderr)

    # A refusal must not be reported as success: the tree was SKIPPED, and
    # "Synchronized N trees" would read as though it had been handled.
    if refused:
        print(
            "A tree is ahead of the canon and was left alone — promote it "
            "before syncing.",
            file=sys.stderr,
        )
        return 1

    if args.command == "check":
        if drift:
            print("DRIFT — run sync, or promote project|package.", file=sys.stderr)
            return 1
        print(
            f"OK — the canon ({format_version(read_version(canon))}) and "
            f"{len(targets)} tree(s) are synchronized."
        )
        return 0

    if args.dry_run:
        print("DRY RUN — nothing was written.")
        return 0

    print(
        f"Synchronized {len(targets)} tree(s) from the canon "
        f"({format_version(read_version(canon))})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
