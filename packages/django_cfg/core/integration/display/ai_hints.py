"""
AI Hints display manager for Django CFG.

Displays helpful hints for AI assistants (Claude, GPT, etc.) in console output.
These hints help AI understand Django 5.2+ async patterns and best practices.
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .base import BaseDisplayManager


# AI Hints registry - can be extended
AI_HINTS = [
    {
        "id": "djangocfg_mcp_docs",
        "title": "DjangoCFG MCP Docs",
        "category": "docs",
        "priority": "high",
        "hint": "DjangoCFG docs available via MCP server for AI assistants",
        "example": "django-cfg search \"database config\"",
        "docs": "https://mcp.djangocfg.com/mcp",
    },
    {
        "id": "django_async_orm",
        "title": "Django 5.2 Async ORM",
        "category": "async",
        "priority": "high",
        "hint": "Use a-prefixed methods in async contexts: aget(), acreate(), aupdate(), adelete(), acount(), aexists()",
        "example": "await Model.objects.aget(id=1)  # NOT Model.objects.get(id=1)",
        "docs": "https://docs.djangoproject.com/en/5.2/topics/async/",
    },
    {
        "id": "django_async_iteration",
        "title": "Async QuerySet Iteration",
        "category": "async",
        "priority": "high",
        "hint": "Use 'async for' for QuerySet iteration in async contexts",
        "example": "async for obj in Model.objects.filter(...): ...",
        "docs": None,
    },
    {
        "id": "django_sync_to_async",
        "title": "Sync to Async Conversion",
        "category": "async",
        "priority": "medium",
        "hint": "Use sync_to_async() for calling sync functions from async context",
        "example": "from asgiref.sync import sync_to_async\nawait sync_to_async(sync_function)()",
        "docs": None,
    },
    {
        "id": "pydantic_rpc_params",
        "title": "Pydantic for RPC Params",
        "category": "typing",
        "priority": "medium",
        "hint": "Use Pydantic models instead of Optional[dict] for RPC handler params",
        "example": "async def handler(conn, params: MyParamsModel) -> MyResultModel:",
        "docs": None,
    },
]


class AIHintsDisplayManager(BaseDisplayManager):
    """Manager for displaying AI hints in console."""

    def __init__(self, config=None):
        """Initialize AI hints display manager."""
        super().__init__(config)
        self._hints = AI_HINTS

    def display_ai_hints(self, mode: str = "short"):
        """
        Display AI hints based on mode.

        Args:
            mode: "short" for compact view, "full" for detailed view
        """
        if mode == "short":
            self._display_hints_short()
        else:
            self._display_hints_full()

    def _display_hints_short(self):
        """Display compact AI hints."""
        # Always show MCP docs hint first
        mcp_hint = next((h for h in self._hints if h.get("id") == "djangocfg_mcp_docs"), None)

        hints_text = Text()
        hints_text.append("🤖 AI Docs: ", style="bold magenta")

        if mcp_hint:
            hints_text.append("MCP ", style="cyan")
            hints_text.append(mcp_hint.get("docs", "https://mcp.djangocfg.com/mcp"), style="bright_blue underline")
            hints_text.append(" | ", style="dim")
            hints_text.append("django-cfg search \"query\"", style="dim")

        self.console.print(hints_text)

    def _display_hints_full(self):
        """Display detailed AI hints."""
        if not self._hints:
            return

        # Group hints by category
        categories = {}
        for hint in self._hints:
            cat = hint.get("category", "general")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(hint)

        # Create hints table
        hints_table = self.create_table()
        hints_table.add_column("Hint", style="bright_cyan", width=35)
        hints_table.add_column("Details", style="white")

        for category, hints in categories.items():
            # Add category header
            hints_table.add_row(
                f"[bold magenta]━━ {category.upper()} ━━[/bold magenta]",
                ""
            )

            for hint in hints:
                priority_badge = {
                    "high": "[red]●[/red]",
                    "medium": "[yellow]●[/yellow]",
                    "low": "[green]●[/green]",
                }.get(hint.get("priority", "low"), "●")

                title = f"{priority_badge} {hint['title']}"

                details = hint["hint"]
                if hint.get("example"):
                    details += f"\n[dim]Example: {hint['example']}[/dim]"

                hints_table.add_row(title, details)

        hints_panel = self.create_full_width_panel(
            hints_table,
            title="🤖 AI Development Hints (Django 5.2+)",
            border_style="magenta"
        )

        self.console.print(hints_panel)

    def get_hints_for_context(self, context: str = None) -> list:
        """
        Get hints relevant to a specific context.

        Args:
            context: Optional context filter (e.g., "async", "typing")

        Returns:
            List of relevant hints
        """
        if not context:
            return self._hints

        return [h for h in self._hints if h.get("category") == context]

    def add_hint(self, hint: dict):
        """
        Add a custom hint to the registry.

        Args:
            hint: Dict with keys: id, title, category, priority, hint, example, docs
        """
        required_keys = {"id", "title", "hint"}
        if not required_keys.issubset(hint.keys()):
            raise ValueError(f"Hint must have keys: {required_keys}")

        # Avoid duplicates
        if not any(h["id"] == hint["id"] for h in self._hints):
            self._hints.append(hint)


def get_ai_hints_manager(config=None) -> AIHintsDisplayManager:
    """Get AI hints display manager instance."""
    return AIHintsDisplayManager(config)
