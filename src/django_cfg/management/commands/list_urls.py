"""
Show URLs Command

Display all available URLs in the Django project with Rich formatting.
Useful for development and webhook configuration.
"""

import re
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.conf import settings

# Rich imports for beautiful output
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align

from django_cfg.core.config import get_current_config


class Command(BaseCommand):
    """Command to display all available URLs in the project."""
    help = "Display all available URLs with Rich formatting"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.config = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--filter",
            type=str,
            help="Filter URLs containing this string",
            default=None
        )
        parser.add_argument(
            "--webhook",
            action="store_true",
            help="Show only webhook-related URLs"
        )
        parser.add_argument(
            "--api",
            action="store_true",
            help="Show only API URLs"
        )
        parser.add_argument(
            "--with-ngrok",
            action="store_true",
            help="Show ngrok URLs alongside local URLs"
        )

    def handle(self, *args, **options):
        filter_str = options["filter"]
        webhook_only = options["webhook"]
        api_only = options["api"]
        with_ngrok = options["with_ngrok"]

        # Show header
        self.show_header()

        # Load config
        self.load_config()

        # Get all URLs
        urls = self.get_all_urls()

        # Filter URLs
        if filter_str:
            urls = [url for url in urls if filter_str.lower() in url['pattern'].lower()]
        
        if webhook_only:
            urls = [url for url in urls if 'webhook' in url['pattern'].lower() or 'hook' in url['pattern'].lower()]
        
        if api_only:
            urls = [url for url in urls if '/api/' in url['pattern'] or url['pattern'].startswith('api/')]

        # Display URLs
        self.display_urls(urls, with_ngrok)

        # Show webhook info if requested
        if webhook_only or with_ngrok:
            self.show_webhook_info()

    def show_header(self):
        """Show beautiful header with Rich."""
        title = Text("Django URLs Overview", style="bold cyan")
        subtitle = Text("All available URLs in your project", style="dim")
        
        header_content = Align.center(
            Text.assemble(
                title, "\n",
                subtitle
            )
        )
        
        self.console.print()
        self.console.print(Panel(
            header_content,
            title="🔗 URL Inspector",
            border_style="bright_blue",
            padding=(1, 2)
        ))

    def load_config(self):
        """Load Django CFG configuration."""
        try:
            self.config = get_current_config()
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Failed to load config: {e}[/yellow]")
            self.config = None

    def get_all_urls(self):
        """Extract all URLs from Django URL configuration."""
        urls = []
        resolver = get_resolver()
        
        def extract_urls(url_patterns, prefix=''):
            for pattern in url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    # This is an include() - recurse
                    new_prefix = prefix + str(pattern.pattern)
                    extract_urls(pattern.url_patterns, new_prefix)
                else:
                    # This is a regular URL pattern
                    full_pattern = prefix + str(pattern.pattern)
                    
                    # Clean up the pattern
                    clean_pattern = re.sub(r'\^|\$', '', full_pattern)
                    clean_pattern = re.sub(r'\\/', '/', clean_pattern)
                    
                    # Get view info
                    view_name = getattr(pattern, 'name', None)
                    view_func = getattr(pattern, 'callback', None)
                    
                    if view_func:
                        if hasattr(view_func, 'view_class'):
                            # Class-based view
                            view_info = f"{view_func.view_class.__name__}"
                            module = view_func.view_class.__module__
                        elif hasattr(view_func, '__name__'):
                            # Function-based view
                            view_info = f"{view_func.__name__}()"
                            module = getattr(view_func, '__module__', 'unknown')
                        else:
                            view_info = str(view_func)
                            module = 'unknown'
                    else:
                        view_info = 'Unknown'
                        module = 'unknown'
                    
                    urls.append({
                        'pattern': clean_pattern,
                        'name': view_name,
                        'view': view_info,
                        'module': module
                    })
        
        extract_urls(resolver.url_patterns)
        return urls

    def display_urls(self, urls, with_ngrok=False):
        """Display URLs in a Rich table."""
        if not urls:
            self.console.print("[yellow]No URLs found matching the criteria.[/yellow]")
            return

        # Create table
        table = Table(title=f"🔗 Found {len(urls)} URLs", show_header=True, header_style="bold cyan")
        table.add_column("URL Pattern", style="cyan", width=40)
        table.add_column("Name", style="white", width=20)
        table.add_column("View", style="green", width=25)
        
        if with_ngrok:
            table.add_column("Ngrok URL", style="magenta", width=40)

        # Get base URLs
        base_url = self.get_base_url()
        ngrok_url = self.get_ngrok_url() if with_ngrok else None

        # Add rows
        for url in urls[:50]:  # Limit to first 50 URLs
            pattern = url['pattern']
            name = url['name'] or '—'
            view = url['view']
            
            # Truncate long view names
            if len(view) > 23:
                view = view[:20] + "..."
            
            row = [pattern, name, view]
            
            if with_ngrok:
                if ngrok_url:
                    full_ngrok_url = f"{ngrok_url.rstrip('/')}/{pattern.lstrip('/')}"
                    row.append(full_ngrok_url)
                else:
                    row.append("—")
            
            table.add_row(*row)

        if len(urls) > 50:
            table.caption = f"Showing first 50 of {len(urls)} URLs"

        self.console.print(table)

        # Show base URL info
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Info", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("🌐 Base URL:", base_url)
        if with_ngrok and ngrok_url:
            info_table.add_row("🔗 Ngrok URL:", ngrok_url)
        
        self.console.print()
        self.console.print(info_table)

    def show_webhook_info(self):
        """Show webhook-specific information using reverse."""
        self.console.print()
        
        webhook_table = Table(title="🔔 Webhook Configuration", show_header=True, header_style="bold yellow")
        webhook_table.add_column("Service", style="white", width=25)
        webhook_table.add_column("Local URL", style="cyan", width=60)
        webhook_table.add_column("Ngrok URL", style="magenta", width=60)
        
        base_url = self.get_base_url()
        ngrok_url = self.get_ngrok_url()
        
        # Get webhook URLs using reverse
        try:
            from django.urls import reverse
            
            # Common webhook endpoints with their URL names
            webhooks = [
                ("Twilio Message Status", "cfg_accounts:webhook-message-status"),
                ("Twilio Verification", "cfg_accounts:webhook-verification-status"),
            ]
            
            for service, url_name in webhooks:
                try:
                    # Get the reversed URL path
                    url_path = reverse(url_name)
                    
                    # Build full URLs
                    local_full = f"{base_url.rstrip('/')}{url_path}"
                    ngrok_full = f"{ngrok_url.rstrip('/')}{url_path}" if ngrok_url else "—"
                    
                    webhook_table.add_row(service, local_full, ngrok_full)
                    
                except Exception as e:
                    # Fallback if reverse fails
                    self.console.print(f"[yellow]⚠️  Could not reverse URL for {service}: {e}[/yellow]")
                    fallback_path = f"/api/accounts/webhook/{service.lower().replace(' ', '-').replace('twilio ', '')}/"
                    local_full = f"{base_url.rstrip('/')}{fallback_path}"
                    ngrok_full = f"{ngrok_url.rstrip('/')}{fallback_path}" if ngrok_url else "—"
                    webhook_table.add_row(service, local_full, ngrok_full)
            
        except ImportError:
            # Fallback if Django is not available
            webhooks = [
                ("Twilio Message Status", "/api/accounts/webhook/message-status/"),
                ("Twilio Verification", "/api/accounts/webhook/verification-status/"),
            ]
            
            for service, endpoint in webhooks:
                local_full = f"{base_url.rstrip('/')}{endpoint}"
                ngrok_full = f"{ngrok_url.rstrip('/')}{endpoint}" if ngrok_url else "—"
                webhook_table.add_row(service, local_full, ngrok_full)
        
        self.console.print(webhook_table)
        
        # Show tips
        tips = [
            "💡 Use ngrok URLs for webhook configuration in production services",
            "🔒 Always validate webhook signatures in production",
            "📝 Test webhooks using the test_twilio management command",
        ]
        
        for tip in tips:
            self.console.print(f"[dim]{tip}[/dim]")

    def get_base_url(self):
        """Get base URL for the application."""
        if self.config:
            return self.config.api_url
        else:
            # Fallback to Django settings
            debug = getattr(settings, 'DEBUG', True)
            if debug:
                return "http://localhost:8000"
            else:
                return "https://yourdomain.com"

    def get_ngrok_url(self):
        """Get ngrok URL if available."""
        if self.config:
            return self.config.get_ngrok_url()
        return None