"""
Django CFG Search Command

Search DjangoCFG documentation without loading Django.
"""

import json
import click


@click.command()
@click.argument("query")
@click.option("--limit", "-l", default=5, help="Maximum number of results (default: 5)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--full", "-f", is_flag=True, help="Show full content without truncation")
def search(query: str, limit: int, as_json: bool, full: bool):
    """
    🔍 Search DjangoCFG documentation

    Fast documentation search without loading Django.

    \b
    Examples:
        django-cfg search "database configuration"
        django-cfg search "redis cache" --limit 3
        django-cfg search "email smtp" --json

    \b
    Python API:
        from django_cfg.modules.django_ai import search, get_docs
        results = search("database")
        docs = get_docs("How to configure PostgreSQL?")

    \b
    MCP Server:
        https://mcp.djangocfg.com/mcp
    """
    from django_cfg.modules.django_ai import search as do_search
    from django_cfg.modules.django_ai.client import DocsClientError

    if not as_json:
        click.echo(f"🔍 Searching: {query}\n")

    try:
        results = do_search(query, limit)

        if not results:
            if as_json:
                click.echo(json.dumps({"results": [], "query": query}))
            else:
                click.echo(click.style("No results found.", fg="yellow"))
            return

        if as_json:
            output = {
                "query": query,
                "results": [r.to_dict() for r in results]
            }
            click.echo(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            for i, r in enumerate(results, 1):
                click.echo(click.style(f"{i}. {r.title}", fg="green", bold=True))

                # Truncate content unless --full flag is set
                if full:
                    content = r.content
                else:
                    content = r.content[:1000] + "..." if len(r.content) > 1000 else r.content
                click.echo(f"   {content}")

                if r.url:
                    click.echo(click.style(f"   → {r.url}", fg="cyan"))
                click.echo()

    except DocsClientError as e:
        if as_json:
            click.echo(json.dumps({"error": str(e)}))
        else:
            click.echo(click.style(f"Error: {e}", fg="red"))
        raise SystemExit(1)
