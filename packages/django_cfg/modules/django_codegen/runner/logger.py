"""
Rich logging for code generation.

Provides beautiful console output with:
- Progress bars for long operations
- Tables for summaries
- Colored status indicators
- Spinners for operations in progress
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class LogLevel(str, Enum):
    """Log level for generation."""

    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class GenerationStats:
    """Statistics for generation run."""

    groups_generated: int = 0
    groups_copied: int = 0
    files_written: int = 0
    targets_processed: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


class GenerationLogger:
    """Rich logger for code generation."""

    def __init__(
        self,
        console: Console | None = None,
        verbose: bool = False,
        quiet: bool = False,
    ):
        """
        Initialize logger.

        Args:
            console: Rich console instance (creates new if None)
            verbose: Show debug messages
            quiet: Only show errors and warnings
        """
        self.console = console or Console()
        self.verbose = verbose
        self.quiet = quiet
        self.stats = GenerationStats()
        self._progress: Progress | None = None
        self._current_task_id: Any = None

    # -------------------------------------------------------------------------
    # Basic logging
    # -------------------------------------------------------------------------

    def debug(self, message: str) -> None:
        """Log debug message (only if verbose)."""
        if self.verbose:
            self.console.print(f"[dim]{message}[/dim]")

    def info(self, message: str) -> None:
        """Log info message."""
        if not self.quiet:
            self.console.print(message)

    def success(self, message: str) -> None:
        """Log success message with checkmark."""
        if not self.quiet:
            self.console.print(f"[green]✓[/green] {message}")

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.console.print(f"[yellow]⚠[/yellow] {message}")
        self.stats.warnings.append(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.console.print(f"[red]✗[/red] {message}")
        self.stats.errors.append(message)

    def skip(self, message: str) -> None:
        """Log skipped item."""
        if self.verbose:
            self.console.print(f"[dim]⊘ {message}[/dim]")
        self.stats.skipped.append(message)

    # -------------------------------------------------------------------------
    # Headers and sections
    # -------------------------------------------------------------------------

    def header(self, title: str, subtitle: str | None = None) -> None:
        """Print section header."""
        if self.quiet:
            return

        text = Text()
        text.append(f"\n{title}", style="bold cyan")
        if subtitle:
            text.append(f" ({subtitle})", style="dim")

        self.console.print(text)
        self.console.print("─" * min(len(title) + (len(subtitle) + 3 if subtitle else 0), 60), style="dim")

    def subheader(self, title: str) -> None:
        """Print subsection header."""
        if not self.quiet:
            self.console.print(f"\n[bold]{title}[/bold]")

    def section_start(self, name: str) -> None:
        """Start a new section with panel."""
        if not self.quiet:
            self.console.print()
            self.console.rule(f"[bold blue]{name}[/bold blue]")

    def section_end(self) -> None:
        """End current section."""
        if not self.quiet:
            self.console.print()

    # -------------------------------------------------------------------------
    # Progress tracking
    # -------------------------------------------------------------------------

    def progress_start(self, description: str, total: int) -> None:
        """Start progress bar."""
        if self.quiet:
            return

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        )
        self._progress.start()
        self._current_task_id = self._progress.add_task(description, total=total)

    def progress_update(self, advance: int = 1, description: str | None = None) -> None:
        """Update progress bar."""
        if self._progress and self._current_task_id is not None:
            kwargs: dict[str, Any] = {"advance": advance}
            if description:
                kwargs["description"] = description
            self._progress.update(self._current_task_id, **kwargs)

    def progress_stop(self) -> None:
        """Stop progress bar."""
        if self._progress:
            self._progress.stop()
            self._progress = None
            self._current_task_id = None

    # -------------------------------------------------------------------------
    # Spinners for operations
    # -------------------------------------------------------------------------

    def spinner(self, message: str) -> "SpinnerContext":
        """Create a spinner context manager."""
        return SpinnerContext(self.console, message, quiet=self.quiet)

    # -------------------------------------------------------------------------
    # Tables and summaries
    # -------------------------------------------------------------------------

    def table(
        self,
        title: str,
        columns: list[str],
        rows: list[list[str]],
        styles: list[str] | None = None,
    ) -> None:
        """Print a table."""
        if self.quiet:
            return

        table = Table(title=title)
        styles = styles or [""] * len(columns)

        for col, style in zip(columns, styles):
            table.add_column(col, style=style)

        for row in rows:
            table.add_row(*row)

        self.console.print(table)

    def tree(self, title: str, items: dict[str, list[str]]) -> None:
        """Print a tree structure."""
        if self.quiet:
            return

        tree = Tree(f"[bold]{title}[/bold]")
        for parent, children in items.items():
            branch = tree.add(f"[cyan]{parent}[/cyan]")
            for child in children:
                branch.add(f"[dim]{child}[/dim]")

        self.console.print(tree)

    def summary(self, title: str = "Generation Summary") -> None:
        """Print generation summary with stats."""
        if self.quiet and not self.stats.errors:
            return

        # Build summary table
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")

        if self.stats.groups_generated > 0:
            table.add_row("Groups generated", f"[green]{self.stats.groups_generated}[/green]")
        if self.stats.groups_copied > 0:
            table.add_row("Groups copied", f"[green]{self.stats.groups_copied}[/green]")
        if self.stats.files_written > 0:
            table.add_row("Files written", f"[cyan]{self.stats.files_written}[/cyan]")
        if self.stats.targets_processed > 0:
            table.add_row("Targets processed", f"[cyan]{self.stats.targets_processed}[/cyan]")
        if self.stats.skipped:
            table.add_row("Skipped", f"[dim]{len(self.stats.skipped)}[/dim]")
        if self.stats.warnings:
            table.add_row("Warnings", f"[yellow]{len(self.stats.warnings)}[/yellow]")
        if self.stats.errors:
            table.add_row("Errors", f"[red]{len(self.stats.errors)}[/red]")

        # Determine panel style
        if self.stats.errors:
            border_style = "red"
            status = "[red]Failed[/red]"
        elif self.stats.warnings:
            border_style = "yellow"
            status = "[yellow]Completed with warnings[/yellow]"
        else:
            border_style = "green"
            status = "[green]Success[/green]"

        # Print panel
        self.console.print()
        panel = Panel(
            table,
            title=f"[bold]{title}[/bold]",
            subtitle=status,
            border_style=border_style,
        )
        self.console.print(panel)

    # -------------------------------------------------------------------------
    # Generation-specific methods
    # -------------------------------------------------------------------------

    def gen_start(self, generator: str, language: str | None = None) -> None:
        """Log generation start."""
        if language:
            self.header(f"{generator}", language)
        else:
            self.header(generator)

    def gen_groups(self, groups: list[str], label: str = "Groups") -> None:
        """Log groups being processed."""
        if self.quiet:
            return

        if len(groups) <= 10:
            self.info(f"  {label}: [cyan]{', '.join(sorted(groups))}[/cyan]")
        else:
            self.info(f"  {label}: [cyan]{len(groups)} groups[/cyan]")
            if self.verbose:
                for group in sorted(groups):
                    self.debug(f"    - {group}")

    def gen_wildcards(self, patterns: list[str]) -> None:
        """Log wildcard patterns."""
        if patterns and not self.quiet:
            self.info(f"  Wildcard patterns: [yellow]{', '.join(patterns)}[/yellow]")

    def gen_target(self, target_type: str, path: Path, language: str | None = None) -> None:
        """Log target being processed."""
        msg = f"  Target: [bold]{target_type}[/bold]"
        if language:
            msg += f" ([cyan]{language}[/cyan])"
        msg += f" -> {path}"
        self.info(msg)
        self.stats.targets_processed += 1

    def gen_copy(self, source: Path, target: Path, count: int) -> None:
        """Log copy operation."""
        self.debug(f"    Copy: {source.name} -> {target}")
        self.stats.groups_copied += count

    def gen_clean(self, path: Path) -> None:
        """Log clean operation."""
        self.debug(f"    Clean: {path}")

    def gen_command(self, command: str) -> None:
        """Log command execution."""
        self.debug(f"    Run: {command}")

    def gen_file(self, path: Path) -> None:
        """Log file written."""
        self.stats.files_written += 1
        if self.verbose:
            self.debug(f"    Write: {path.name}")

    def gen_complete(self, count: int, label: str = "groups") -> None:
        """Log generation complete for a section."""
        self.stats.groups_generated += count
        self.success(f"Generated {count} {label}")


class SpinnerContext:
    """Context manager for spinner."""

    def __init__(self, console: Console, message: str, quiet: bool = False):
        self.console = console
        self.message = message
        self.quiet = quiet
        self._progress: Progress | None = None
        self._task_id: Any = None

    def __enter__(self) -> "SpinnerContext":
        if not self.quiet:
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True,
            )
            self._progress.start()
            self._task_id = self._progress.add_task(self.message)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._progress:
            self._progress.stop()

    def update(self, message: str) -> None:
        """Update spinner message."""
        if self._progress and self._task_id is not None:
            self._progress.update(self._task_id, description=message)


# -------------------------------------------------------------------------
# Global instance and convenience functions
# -------------------------------------------------------------------------

_logger: GenerationLogger | None = None


def get_generation_logger(
    console: Console | None = None,
    verbose: bool = False,
    quiet: bool = False,
    reset: bool = False,
) -> GenerationLogger:
    """
    Get global generation logger instance.

    Args:
        console: Rich console instance
        verbose: Show debug messages
        quiet: Only show errors
        reset: Force create new instance

    Returns:
        GenerationLogger instance
    """
    global _logger
    if _logger is None or reset:
        _logger = GenerationLogger(console=console, verbose=verbose, quiet=quiet)
    return _logger


def reset_generation_logger() -> None:
    """Reset global logger instance."""
    global _logger
    _logger = None
