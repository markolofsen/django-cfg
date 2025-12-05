"""
AI Documentation Command

Search and retrieve DjangoCFG documentation for AI assistants.

Usage:
    poetry run python manage.py ai_docs search "How to configure database?"
    poetry run python manage.py ai_docs info DatabaseConfig
    poetry run python manage.py ai_docs mcp
"""

import json

from django_cfg.management.utils import SafeCommand


class Command(SafeCommand):
    """Command to search DjangoCFG documentation."""

    command_name = "ai_docs"
    help = "Search DjangoCFG documentation (AI-friendly)"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="action", help="Action to perform")

        # Search subcommand
        search_parser = subparsers.add_parser("search", help="Search documentation")
        search_parser.add_argument(
            "query",
            type=str,
            help="Search query",
        )
        search_parser.add_argument(
            "--limit",
            type=int,
            default=5,
            help="Maximum number of results (default: 5)",
        )
        search_parser.add_argument(
            "--json",
            action="store_true",
            dest="as_json",
            help="Output as JSON",
        )

        # Info subcommand
        info_parser = subparsers.add_parser("info", help="Get info about a topic")
        info_parser.add_argument(
            "topic",
            type=str,
            help="Topic name (e.g., DatabaseConfig)",
        )
        info_parser.add_argument(
            "--json",
            action="store_true",
            dest="as_json",
            help="Output as JSON",
        )

        # MCP config subcommand
        subparsers.add_parser("mcp", help="Show MCP server configuration")

        # Hint subcommand
        subparsers.add_parser("hint", help="Show AI hint for using documentation")

    def handle(self, *args, **options):
        action = options.get("action")

        if action == "search":
            self._handle_search(options)
        elif action == "info":
            self._handle_info(options)
        elif action == "mcp":
            self._handle_mcp()
        elif action == "hint":
            self._handle_hint()
        else:
            self._handle_default()

    def _handle_search(self, options):
        """Handle search action."""
        from django_cfg.modules.django_ai import search, DjangoCfgDocsClient
        from django_cfg.modules.django_ai.client import DocsClientError

        query = options["query"]
        limit = options["limit"]
        as_json = options.get("as_json", False)

        self.stdout.write(f"Searching: {query}\n")

        try:
            results = search(query, limit)

            if not results:
                self.stdout.write(self.style.WARNING("No results found."))
                return

            if as_json:
                output = [r.to_dict() for r in results]
                self.stdout.write(json.dumps(output, indent=2, ensure_ascii=False))
            else:
                for i, r in enumerate(results, 1):
                    self.stdout.write(self.style.SUCCESS(f"\n{i}. {r.title}"))
                    self.stdout.write(f"   {r.content[:200]}...")
                    if r.url:
                        self.stdout.write(self.style.HTTP_INFO(f"   {r.url}"))

        except DocsClientError as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def _handle_info(self, options):
        """Handle info action."""
        from django_cfg.modules.django_ai import get_info
        from django_cfg.modules.django_ai.client import DocsClientError

        topic = options["topic"]
        as_json = options.get("as_json", False)

        self.stdout.write(f"Getting info: {topic}\n")

        try:
            info = get_info(topic)

            if as_json:
                self.stdout.write(json.dumps(info, indent=2, ensure_ascii=False))
            else:
                self.stdout.write(self.style.SUCCESS(f"\n{topic}"))
                for key, value in info.items():
                    self.stdout.write(f"  {key}: {value}")

        except DocsClientError as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def _handle_mcp(self):
        """Handle MCP config action."""
        from django_cfg.modules.django_ai import DjangoCfgDocsClient

        client = DjangoCfgDocsClient()
        config = client.get_mcp_config()

        self.stdout.write(self.style.SUCCESS("\nMCP Server Configuration:"))
        self.stdout.write(json.dumps(config, indent=2))

        self.stdout.write(self.style.HTTP_INFO(
            "\nAdd this to your AI assistant configuration to enable DjangoCFG documentation access."
        ))

    def _handle_hint(self):
        """Handle hint action."""
        from django_cfg.modules.django_ai import AI_HINT

        self.stdout.write(self.style.SUCCESS("\nAI Documentation Hint:"))
        self.stdout.write(AI_HINT)

    def _handle_default(self):
        """Handle default action (no action specified)."""
        self.stdout.write(self.style.SUCCESS("DjangoCFG AI Documentation"))
        self.stdout.write("")
        self.stdout.write("Usage:")
        self.stdout.write("  poetry run python manage.py ai_docs search \"your query\"")
        self.stdout.write("  poetry run python manage.py ai_docs info DatabaseConfig")
        self.stdout.write("  poetry run python manage.py ai_docs mcp")
        self.stdout.write("  poetry run python manage.py ai_docs hint")
        self.stdout.write("")
        self.stdout.write("For AI assistants:")
        self.stdout.write(self.style.HTTP_INFO("  MCP Server: https://mcp.djangocfg.com/mcp"))
        self.stdout.write(self.style.HTTP_INFO("  Search API: https://mcp.djangocfg.com/api/search?q=QUERY"))
