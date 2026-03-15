"""
Utility functions for runner.

v6.1: Rich logging integration.
"""

from __future__ import annotations

import fnmatch
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

from django_cfg.modules.django_codegen.config import Language

if TYPE_CHECKING:
    from django_cfg.modules.django_codegen.runner.logger import GenerationLogger


def log(msg: str, stdout: Any = None, style: str = "default") -> None:
    """Print message with optional styling (legacy support)."""
    if stdout and hasattr(stdout, "style"):
        if style == "success":
            stdout.write(stdout.style.SUCCESS(msg))
        elif style == "error":
            stdout.write(stdout.style.ERROR(msg))
        elif style == "warning":
            stdout.write(stdout.style.WARNING(msg))
        else:
            stdout.write(msg)
    elif stdout:
        stdout.write(msg)
    else:
        print(msg)


def get_source_dir(lang: Language | str) -> Path:
    """Get source directory for generated files."""
    from django.conf import settings

    lang_value = lang.value if isinstance(lang, Language) else lang
    return Path(settings.BASE_DIR) / "openapi" / "clients" / lang_value


def expand_wildcards(groups: list[str], lang: Language | str) -> list[str]:
    """
    Expand wildcard patterns like cfg_* to actual groups.

    Scans source directory for matching groups.
    """
    source = get_source_dir(lang)
    if not source.exists():
        return [g for g in groups if "*" not in g]

    available = [d.name for d in source.iterdir() if d.is_dir()]

    expanded = []
    for group in groups:
        if "*" in group:
            matches = fnmatch.filter(available, group)
            expanded.extend(matches)
        else:
            expanded.append(group)

    return list(set(expanded))


def run_post_build(
    path: Path,
    command: str,
    logger: GenerationLogger | Any,
) -> None:
    """Run post-build command."""
    # Find package root (go up from generated dir)
    package_root = path
    while package_root.parent != package_root:
        if (package_root / "package.json").exists():
            break
        package_root = package_root.parent

    # Use logger if available
    if hasattr(logger, "gen_command"):
        logger.gen_command(f"{command} in {package_root.name}")
    else:
        log(f"  Running: {command} in {package_root.name}", logger)

    result = subprocess.run(
        command.split(),
        cwd=package_root,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        if hasattr(logger, "success"):
            logger.success("Post-build completed")
        else:
            log("  Post-build completed", logger, "success")
    else:
        if hasattr(logger, "warning"):
            logger.warning(f"Post-build failed: {result.stderr[:200]}")
        else:
            log(f"  Post-build failed: {result.stderr[:200]}", logger, "warning")


def clean_target(
    target: Path,
    logger: GenerationLogger | Any = None,
) -> None:
    """
    Clean target directory before copying.

    Removes all contents but keeps the directory itself.
    """
    if not target.exists():
        return

    for item in target.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    if logger:
        if hasattr(logger, "gen_clean"):
            logger.gen_clean(target)
        else:
            log(f"  Cleaned: {target}", logger)


def copy_groups(
    source: Path,
    target: Path,
    groups: list[str],
    logger: GenerationLogger | Any,
    *,
    clean_first: bool = True,
) -> int:
    """
    Copy group directories from source to target.

    Args:
        source: Source directory containing group folders
        target: Target directory to copy to
        groups: List of group names to copy
        logger: GenerationLogger or Django stdout for logging
        clean_first: If True, clean target directory before copying (default: True)

    Returns:
        Number of groups copied
    """
    # Clean target directory first
    if clean_first and target.exists():
        clean_target(target, logger)

    copied = 0

    for group in groups:
        src = source / group
        dst = target / group

        if not src.exists():
            if hasattr(logger, "warning"):
                logger.warning(f"Source not found: {src}")
            else:
                log(f"  Warning: source not found {src}", logger, "warning")
            continue

        if dst.exists():
            shutil.rmtree(dst)

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst)
        copied += 1

    if hasattr(logger, "gen_copy"):
        logger.gen_copy(source, target, copied)

    return copied


GO_STDLIB_PACKAGES = frozenset({
    "archive", "bufio", "bytes", "cmp", "compress", "container", "context",
    "crypto", "database", "debug", "embed", "encoding", "errors", "expvar",
    "flag", "fmt", "go", "hash", "html", "image", "io", "iter", "log",
    "maps", "math", "mime", "net", "os", "path", "plugin", "reflect",
    "regexp", "runtime", "slices", "sort", "strconv", "strings", "structs",
    "sync", "syscall", "testing", "text", "time", "unicode", "unique",
    "unsafe",
})


def _is_go_stdlib(import_path: str) -> bool:
    """Check if an import path is a Go standard library package."""
    root = import_path.split("/")[0]
    return root in GO_STDLIB_PACKAGES


def fix_go_imports(
    target: Path,
    module_path: str,
    logger: GenerationLogger | Any,
) -> None:
    """Fix Go import paths in generated files."""
    import re

    if hasattr(logger, "debug"):
        logger.debug(f"Fixing Go imports with module: {module_path}")
    else:
        log(f"  Fixing Go imports with module: {module_path}", logger)

    for go_file in target.rglob("*.go"):
        content = go_file.read_text()
        original = content

        # Fix import blocks
        def replace_import_block(match: re.Match) -> str:
            imports = match.group(1)
            fixed = []
            for line in imports.strip().split("\n"):
                line = line.strip()
                if not line or line.startswith("//"):
                    fixed.append(line)
                    continue

                import_match = re.match(r'^"([^"]+)"', line)
                if import_match:
                    import_path = import_match.group(1)
                    # Fix bare imports: add module prefix
                    # Skip stdlib, already-qualified paths, and dot/slash imports
                    if not import_path.startswith((".", "/", "github.com", "golang.org")) and not _is_go_stdlib(import_path):
                        line = f'"{module_path}/{import_path}"'
                fixed.append(line)

            return f"import (\n{chr(10).join(fixed)}\n)"

        content = re.sub(r"import\s*\((.*?)\)", replace_import_block, content, flags=re.DOTALL)

        if content != original:
            go_file.write_text(content)

    if hasattr(logger, "success"):
        logger.success("Go imports fixed")
    else:
        log("  Go imports fixed", logger, "success")
