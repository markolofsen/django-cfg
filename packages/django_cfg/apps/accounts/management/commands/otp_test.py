"""
Management command to test OTP functionality.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ...services.otp_service import OTPService
from ...models import CustomUser, OTPSecret


class Command(BaseCommand):
    help = "Test OTP functionality with email and telegram delivery"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to test OTP with'
        )
        parser.add_argument(
            '--delivery',
            type=str,
            choices=['email', 'telegram', 'both'],
            default='email',
            help='Delivery method for OTP'
        )
        parser.add_argument(
            '--verify',
            type=str,
            help='OTP code to verify'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show OTP statistics'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up expired OTPs'
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        
        if options['stats']:
            self.show_stats()
            return
            
        if options['cleanup']:
            self.cleanup_expired()
            return

        email = options.get('email')
        if not email:
            raise CommandError("Email address is required. Use --email option.")

        if options.get('verify'):
            self.verify_otp(email, options['verify'])
        else:
            self.request_otp(email, options['delivery'])

    def request_otp(self, email: str, delivery_method: str):
        """Request OTP for the given email."""
        self.console.print(Panel(
            f"[bold blue]Testing OTP Request[/bold blue]\n"
            f"Email: {email}\n"
            f"Delivery: {delivery_method}",
            title="🔐 OTP Test"
        ))

        try:
            success, error_type = OTPService.request_otp(
                email=email,
                delivery_method=delivery_method,
                source_url="test_command",
                request_ip="127.0.0.1",
                user_agent="test-command/1.0"
            )

            if success:
                self.console.print("[green]✅ OTP request successful![/green]")
                
                # Show the generated OTP for testing
                otp = OTPSecret.objects.filter(
                    email=email.lower().strip(),
                    is_used=False,
                    expires_at__gt=timezone.now()
                ).first()
                
                if otp:
                    self.console.print(f"[yellow]🔑 Generated OTP: {otp.secret}[/yellow]")
                    self.console.print(f"[dim]Expires at: {otp.expires_at}[/dim]")
                    
            else:
                self.console.print(f"[red]❌ OTP request failed: {error_type}[/red]")

        except Exception as e:
            self.console.print(f"[red]❌ Error: {str(e)}[/red]")

    def verify_otp(self, email: str, otp_code: str):
        """Verify OTP for the given email."""
        self.console.print(Panel(
            f"[bold blue]Testing OTP Verification[/bold blue]\n"
            f"Email: {email}\n"
            f"Code: {otp_code}",
            title="✅ OTP Verification"
        ))

        try:
            user = OTPService.verify_otp(
                email=email,
                otp_code=otp_code,
                source_url="test_command",
                request_ip="127.0.0.1",
                user_agent="test-command/1.0"
            )

            if user:
                self.console.print("[green]✅ OTP verification successful![/green]")
                self.console.print(f"[blue]User: {user.email}[/blue]")
                self.console.print(f"[blue]Name: {user.get_full_name() or 'Not set'}[/blue]")
            else:
                self.console.print("[red]❌ OTP verification failed![/red]")

        except Exception as e:
            self.console.print(f"[red]❌ Error: {str(e)}[/red]")

    def show_stats(self):
        """Show OTP statistics."""
        self.console.print(Panel(
            "[bold blue]OTP Statistics[/bold blue]",
            title="📊 Stats"
        ))

        try:
            stats = OTPService.get_otp_stats()
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", justify="right", style="green")

            table.add_row("Total OTPs", str(stats['total_otps']))
            table.add_row("Active OTPs", str(stats['active_otps']))
            table.add_row("Used OTPs", str(stats['used_otps']))
            table.add_row("Expired OTPs", str(stats['expired_otps']))
            table.add_row("Recent (24h)", str(stats['recent_otps_24h']))

            self.console.print(table)

            # Show recent OTPs
            recent_otps = OTPSecret.objects.order_by('-created_at')[:10]
            if recent_otps:
                self.console.print("\n[bold]Recent OTPs:[/bold]")
                otp_table = Table(show_header=True, header_style="bold magenta")
                otp_table.add_column("Email", style="cyan")
                otp_table.add_column("Code", style="yellow")
                otp_table.add_column("Status", style="green")
                otp_table.add_column("Created", style="dim")

                for otp in recent_otps:
                    status = "✅ Valid" if otp.is_valid else ("🔒 Used" if otp.is_used else "⏰ Expired")
                    otp_table.add_row(
                        otp.email,
                        otp.secret,
                        status,
                        otp.created_at.strftime("%H:%M:%S")
                    )

                self.console.print(otp_table)

        except Exception as e:
            self.console.print(f"[red]❌ Error getting stats: {str(e)}[/red]")

    def cleanup_expired(self):
        """Clean up expired OTPs."""
        self.console.print(Panel(
            "[bold blue]Cleaning up expired OTPs[/bold blue]",
            title="🧹 Cleanup"
        ))

        try:
            now = timezone.now()
            expired_otps = OTPSecret.objects.filter(
                is_used=False,
                expires_at__lte=now
            )
            
            count = expired_otps.count()
            expired_otps.delete()
            
            self.console.print(f"[green]✅ Cleaned up {count} expired OTPs[/green]")

        except Exception as e:
            self.console.print(f"[red]❌ Error during cleanup: {str(e)}[/red]")