"""
Startup display manager for Django CFG.
"""

from cmath import e
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import traceback

from .base import BaseDisplayManager
from .ngrok import NgrokDisplayManager
from .ai_hints import AIHintsDisplayManager


class StartupDisplayManager(BaseDisplayManager):
    """Manager for displaying startup information."""

    def __init__(self, config=None):
        """Initialize startup display manager."""
        super().__init__(config)
        self.ngrok_manager = NgrokDisplayManager(config)
        self.ai_hints_manager = AIHintsDisplayManager(config)

    def display_startup_info(self):
        """Display startup information based on config.startup_info_mode."""
        if not self.config:
            return

        # Always check and display ngrok info first if active
        self.ngrok_manager.display_if_active()

        from django_cfg.core.config import StartupInfoMode
        mode = self.config.startup_info_mode

        if mode == StartupInfoMode.NONE:
            self.display_minimal_info()
        elif mode == StartupInfoMode.SHORT:
            self.display_essential_info()
        elif mode == StartupInfoMode.FULL:
            self.display_complete_info()

    def display_minimal_info(self):
        """Display minimal startup info (NONE mode)."""
        try:
            panel_style, env_emoji, env_color = self.get_environment_style()

            # Display beautiful ASCII art banner
            self.print_banner(style="default", color=env_color)
            self.print_spacing()

            # Use reusable header utility
            info_text = self.create_header_text(show_update_check=True)

            # Add startup time if available
            startup_time = self._get_startup_time()
            if startup_time:
                info_text.append(" • ", style="dim")
                info_text.append(f"⚡ {startup_time}", style="green")

            self.console.print(info_text)

            # Show logging info
            self._display_logging_info()
        except Exception as e:
            print(f"❌ ERROR in display_minimal_info: {e}")
            print("🔍 TRACEBACK:")
            traceback.print_exc()
            exit(1)

    def display_essential_info(self):
        """Display essential startup info (SHORT mode)."""
        try:
            panel_style, env_emoji, env_color = self.get_environment_style()

            # Display beautiful ASCII art banner
            self.print_banner(style="default", color=env_color)
            self.print_spacing()

            # Create compact header using reusable utility
            header_text = self.create_header_text(show_update_check=False)

            # Add startup time if available
            startup_time = self._get_startup_time()
            if startup_time:
                header_text.append(" • ", style="dim")
                header_text.append(f"⚡ {startup_time}", style="green")

            header_panel = self.create_panel(
                header_text,
                title="",
                border_style=panel_style,
                width=None
            )
            header_panel.padding = (0, 1)  # Override padding for header
            self.console.print(header_panel)

            # Check for updates first
            self._display_update_notification_short()

            # Create columns for essential info
            self._display_essential_columns()

            # Show logging info
            self._display_logging_info()

            # Display AI hints (short mode)
            self._display_ai_hints(mode="short")
        except Exception as e:
            print(f"❌ ERROR in display_essential_info: {e}")
            print("🔍 TRACEBACK:")
            traceback.print_exc()
            exit(1)

    def display_complete_info(self):
        """Display complete startup info (FULL mode)."""
        try:
            version = self.get_version()
            panel_style, env_emoji, env_color = self.get_environment_style()

            # Display beautiful ASCII art banner
            self.print_banner(style="default", color=env_color)
            self.print_spacing()

            # Get library info
            from django_cfg.config import (
                LIB_SITE_URL,
                LIB_GITHUB_URL,
                LIB_SITE_URL,
                LIB_SUPPORT_URL,
            )

            # Display header using reusable utility
            header_text = self.create_header_text(show_update_check=False)
            self.console.print(header_text)
            self.print_spacing()

            # Create main info table
            info_table = self.create_table()
            info_table.add_column("Setting", style="cyan", width=30)
            info_table.add_column("Value", style="white")

            info_table.add_row("📦 Version", version)
            info_table.add_row("🔗 Prefix", "/cfg/")
            info_table.add_row("🌍 Environment", self.config.env_mode)
            info_table.add_row("🔧 Debug", str(self.config.debug))

            # Show debug_warnings status
            if self.config.debug_warnings:
                info_table.add_row("🔍 Warnings Debug", "[yellow]Enabled (full traceback)[/yellow]")

            info_table.add_row("🏗️ Project", self.config.project_name)

            # Add startup time if available
            startup_time = self._get_startup_time()
            if startup_time:
                info_table.add_row("⚡ Startup Time", f"[green]{startup_time}[/green]")

            # Add environment source
            env_source = getattr(self.config, 'env_mode', 'default_fallback')
            info_table.add_row("🔍 Env Source", env_source)

            info_table.add_row("🌐 Site", LIB_SITE_URL)
            info_table.add_row("📚 Docs", LIB_SITE_URL)
            info_table.add_row("🐙 GitHub", LIB_GITHUB_URL)
            info_table.add_row("🆘 Support", LIB_SUPPORT_URL)

            # Use full URL for health endpoint
            health_url = f"{self.get_base_url()}/cfg/health/"
            info_table.add_row("❤️ Health", health_url)

            # Create main panel with full width
            main_panel = self.create_full_width_panel(
                info_table,
                title=f"{env_emoji} Django CFG Configuration",
                border_style=panel_style
            )

            self.console.print(main_panel)

            # Check for updates
            self._display_update_notification_full()

            # Create columns for apps and endpoints
            self._display_main_columns()

            # App-specific configuration panels
            self._display_config_panels()

            # OpenAPI Client info
            self._display_openapi_client_info()

            # Management commands
            self._display_commands_info()

            # Show logging info
            self._display_logging_info()

            # Display AI hints (full mode)
            self._display_ai_hints(mode="full")

            self.print_spacing()
        except Exception as e:
            print(f"❌ ERROR in display_complete_info: {e}")
            print("🔍 TRACEBACK:")
            traceback.print_exc()
            exit(1)

    def _display_update_notification_short(self):
        """Display update notification for SHORT mode."""
        try:
            from ..version_checker import get_version_info
            version_info = get_version_info()

            if version_info.get('update_available'):
                current = version_info.get('current_version', 'unknown')
                latest = version_info.get('latest_version', 'unknown')

                update_text = Text()
                update_text.append("🚨 Update available: ", style="bold yellow")
                update_text.append(f"{current}", style="red")
                update_text.append(" → ", style="dim")
                update_text.append(f"{latest}", style="green")
                update_text.append("\n💡 Run: ", style="dim")
                update_text.append("poetry add django-cfg@latest", style="bright_blue")

                update_panel = self.create_panel(
                    update_text,
                    title="",
                    border_style="yellow",
                    width=None
                )
                update_panel.padding = (0, 2)  # Override padding
                self.console.print(update_panel)
        except Exception as e:
            print(f"❌ ERROR in _display_update_notification_short: {e}")
            print("🔍 TRACEBACK:")
            traceback.print_exc()
            exit(1)

    def _display_update_notification_full(self):
        """Display update notification for FULL mode."""
        try:
            from ..version_checker import get_version_info
            version_info = get_version_info()

            if version_info.get('update_available'):
                update_table = self.create_table()
                update_table.add_column("Info", style="yellow", width=15)
                update_table.add_column("Value", style="white")

                current = version_info.get('current_version', 'unknown')
                latest = version_info.get('latest_version', 'unknown')
                update_url = version_info.get('update_url', '')

                update_table.add_row("Current", f"[red]{current}[/red]")
                update_table.add_row("Latest", f"[green]{latest}[/green]")
                update_table.add_row("💡 Update", "[bright_blue]poetry add django-cfg@latest[/bright_blue]")
                if update_url:
                    update_table.add_row("PyPI", update_url)

                update_panel = self.create_full_width_panel(
                    update_table,
                    title="🚨 Update Available",
                    border_style="yellow"
                )

                self.console.print(update_panel)
        except Exception:
            pass

    def _display_essential_columns(self):
        """Display essential info in columns for SHORT mode."""
        # Enabled apps
        enabled_apps = self.config.get_installed_apps() if hasattr(self.config, 'get_installed_apps') else []
        apps_table = self.create_table()
        apps_table.add_column("App", style="bright_blue")

        for app in enabled_apps[:5]:  # Limit for SHORT mode
            app_name = app.split('.')[-1]
            apps_table.add_row(f"• {app_name}")

        # Key endpoints
        endpoints_table = self.create_table()
        endpoints_table.add_column("Endpoint", style="bright_green")

        endpoints_table.add_row(f"• {self.get_base_url('cfg', 'health')}")
        endpoints_table.add_row(f"• {self.get_base_url('api', 'payments')}")

        # Use new two-column table method for perfect 50/50 layout
        self.print_two_column_table(
            left_content=apps_table,
            right_content=endpoints_table,
            left_title="📱 Enabled Apps",
            right_title="🔗 Key Endpoints",
            left_style="blue",
            right_style="green"
        )

    def _display_main_columns(self):
        """Display main columns (apps and endpoints) for FULL mode."""
        # Enabled apps
        enabled_apps = self.config.get_installed_apps() if hasattr(self.config, 'get_installed_apps') else []
        apps_table = self.create_table()
        apps_table.add_column("App", style="bright_blue")

        for app in enabled_apps:
            app_name = app.split('.')[-1]
            apps_table.add_row(f"• {app_name}")

        # Endpoints
        endpoints_table = self.create_table()
        endpoints_table.add_column("Endpoint", style="bright_green")

        # Add core endpoints
        endpoints_table.add_row(f"• {self.get_base_url('cfg', 'health')}")
        endpoints_table.add_row(f"• {self.get_base_url('cfg', 'commands')}")

        # Add app-specific API endpoints based on enabled apps
        for app in enabled_apps:
            app_name = app.split('.')[-1]
            if app_name in ['health', 'commands']:
                continue
            else:
                endpoints_table.add_row(f"• {self.get_base_url('api', app_name)}")

        # Use new two-column table method for perfect 50/50 layout
        self.print_two_column_table(
            left_content=apps_table,
            right_content=endpoints_table,
            left_title="📱 Enabled Apps",
            right_title="🔗 Endpoints",
            left_style="blue",
            right_style="green"
        )

    def _display_config_panels(self):
        """Display app-specific configuration panels."""
        config_panels = []

        # Payments configuration
        if (self.config and hasattr(self.config, 'payments') and
            self.config.payments and self.config.payments.enabled):

            payment_table = self.create_table()
            payment_table.add_column("Setting", style="cyan", width=20)
            payment_table.add_column("Value", style="white")

            payment_table.add_row("Enabled", f"[green]{self.config.payments.enabled}[/green]")

            # Show active providers (v2.0)
            active_providers = self.config.payments.active_providers
            if active_providers:
                payment_table.add_row("Providers", f"[green]{', '.join(active_providers)}[/green]")
            else:
                payment_table.add_row("Providers", "[yellow]None configured[/yellow]")

            config_panels.append(self.create_panel(
                payment_table,
                title="💳 Payments",
                border_style="yellow"
            ))

        # Tasks configuration - removed from config_panels, will be shown separately

        # Constance configuration
        try:
            constance_table = self.create_table()
            constance_table.add_column("Setting", style="cyan", width=20)
            constance_table.add_column("Value", style="white")

            # Constance fields moved to separate block
            # Get cache info
            try:
                cache_config = getattr(self.config, 'cache', None)
                if cache_config:
                    constance_table.add_row("Cache", f"[green]{cache_config.backend}[/green]")
                else:
                    constance_table.add_row("Cache", "[yellow]Not configured[/yellow]")
            except Exception:
                constance_table.add_row("Cache", "[red]Error[/red]")

            # Add validation info
            try:
                from django_cfg.core.validation import ConfigurationValidator
                validation_errors = ConfigurationValidator.validate(self.config)
                error_count = len(validation_errors)
                if error_count == 0:
                    constance_table.add_row("Validation", "[green]✓ Valid[/green]")
                else:
                    constance_table.add_row("Validation", f"[red]✗ {error_count} errors[/red]")
            except Exception:
                constance_table.add_row("Validation", "[red]Error[/red]")

            # Add installed apps count
            try:
                installed_apps = self.config.get_installed_apps() if hasattr(self.config, 'get_installed_apps') else []
                constance_table.add_row("Apps", f"[blue]{len(installed_apps)}[/blue]")
            except Exception:
                constance_table.add_row("Apps", "[red]Error[/red]")

            config_panels.append(self.create_panel(
                constance_table,
                title="⚙️ Configuration",
                border_style="cyan"
            ))
        except Exception:
            pass

        # Show config panels
        if len(config_panels) >= 2:
            # Show first two panels in 50/50 layout
            self.print_two_column_table(
                left_content=config_panels[0].renderable,
                right_content=config_panels[1].renderable,
                left_title=config_panels[0].title,
                right_title=config_panels[1].title,
                left_style=config_panels[0].border_style,
                right_style=config_panels[1].border_style
            )

            # Show remaining panels individually
            for panel in config_panels[2:]:
                self.console.print(panel)
        elif config_panels:
            # Show single panel
            for panel in config_panels:
                self.console.print(panel)

        # Show Background Tasks separately
        self._display_background_tasks()

        # Show detailed Constance information (includes summary)
        self._display_constance_details()

    def _display_background_tasks(self):
        """Display Background Tasks information in a separate panel."""
        try:
            # Always show Background Tasks section if config exists
            if not self.config:
                return

            task_table = self.create_table()
            task_table.add_column("Setting", style="cyan", width=20)
            task_table.add_column("Value", style="white")

            # Show real tasks status
            tasks_enabled = self.config.should_enable_rq()
            if tasks_enabled:
                task_table.add_row("Tasks Enabled", "[green]True[/green]")
            else:
                task_table.add_row("Tasks Enabled", "[yellow]False[/yellow]")

            if hasattr(self.config, 'django_rq') and self.config.django_rq:
                queue_names = ', '.join(self.config.django_rq.get_queue_names())
                task_table.add_row("Queues", f"[yellow]{queue_names}[/yellow]")
            else:
                task_table.add_row("Queues", "[yellow]default[/yellow]")

            # Add worker command
            task_table.add_row("Start Workers", "[bright_blue]poetry run python manage.py rqworker default[/bright_blue]")

            task_panel = self.create_full_width_panel(
                task_table,
                title="⚡ Background Tasks",
                border_style="purple"
            )

            self.console.print(task_panel)

        except Exception as e:
            print(f"❌ ERROR in _display_background_tasks: {e}")
            traceback.print_exc()
            exit(1)

    def _display_constance_integrated_block(self, constance_config, all_fields):
        """Display integrated Constance block with summary and field details."""
        try:
            # Create main content table that will contain everything
            main_content = Table(show_header=False, box=None, padding=(0, 1))
            main_content.add_column("Content", justify="left")

            # 1. Add summary section
            summary_table = self.create_table()
            summary_table.add_column("Source", style="cyan", width=20)
            summary_table.add_column("Fields", style="white")

            # Count fields by source
            user_fields = len(constance_config.fields)

            # Count by app (extensions are now auto-discovered)
            tasks_count = 0
            knowbase_count = 0
            payments_count = 0

            try:
                from django_cfg.modules.base import BaseCfgModule
                base_module = BaseCfgModule()

                if base_module.is_extension_enabled("knowbase"):
                    try:
                        from extensions.apps.knowbase.config import (
                            get_django_cfg_knowbase_constance_fields,
                        )
                        knowbase_fields = get_django_cfg_knowbase_constance_fields()
                        knowbase_count = len(knowbase_fields)
                    except:
                        pass

                if base_module.is_extension_enabled("payments"):
                    try:
                        from extensions.apps.payments.config import (
                            get_django_cfg_payments_constance_fields,
                        )
                        payments_fields = get_django_cfg_payments_constance_fields()
                        payments_count = len(payments_fields)
                    except:
                        pass
            except:
                pass

            summary_table.add_row("User Defined", f"[blue]{user_fields}[/blue]")
            if tasks_count > 0:
                summary_table.add_row("Tasks Module", f"[green]{tasks_count}[/green]")
            if knowbase_count > 0:
                summary_table.add_row("Knowbase App", f"[green]{knowbase_count}[/green]")
            if payments_count > 0:
                summary_table.add_row("Payments App", f"[green]{payments_count}[/green]")
            summary_table.add_row("Total", f"[yellow]{len(all_fields)}[/yellow]")

            main_content.add_row(summary_table)
            main_content.add_row("")  # Spacer

            # 2. Add field details section
            groups = {}
            for field in all_fields:
                group = field.group
                if group not in groups:
                    groups[group] = []
                groups[group].append(field)

            group_names = list(groups.keys())[:2]

            if len(group_names) >= 2:
                # Create two-column layout for field details
                details_table = Table(show_header=False, box=None, padding=(0, 2))
                details_table.add_column("Left", justify="left")
                details_table.add_column("Right", justify="left")

                # Left column - first group
                left_table = self.create_table()
                left_table.add_column("Field", style="bright_cyan")
                left_table.add_column("Type", style="yellow")
                for field in groups[group_names[0]][:8]:
                    left_table.add_row(field.name, field.field_type)

                # Right column - second group
                right_table = self.create_table()
                right_table.add_column("Field", style="bright_cyan")
                right_table.add_column("Type", style="yellow")
                for field in groups[group_names[1]][:8]:
                    right_table.add_row(field.name, field.field_type)

                # Create panels for each group
                left_panel = Panel(
                    left_table,
                    title=f"🔧 {group_names[0]} Settings",
                    border_style="cyan",
                    expand=True,
                    padding=(1, 1)
                )

                right_panel = Panel(
                    right_table,
                    title=f"🔧 {group_names[1]} Settings",
                    border_style="blue",
                    expand=True,
                    padding=(1, 1)
                )

                details_table.add_row(left_panel, right_panel)
                main_content.add_row(details_table)

            elif len(group_names) == 1:
                # Single group
                single_table = self.create_table()
                single_table.add_column("Field", style="bright_cyan")
                single_table.add_column("Type", style="yellow")
                single_table.add_column("Default", style="white")

                for field in groups[group_names[0]][:10]:
                    default_str = str(field.default)[:20] + "..." if len(str(field.default)) > 20 else str(field.default)
                    single_table.add_row(field.name, field.field_type, default_str)

                single_panel = Panel(
                    single_table,
                    title=f"🔧 {group_names[0]} Settings",
                    border_style="cyan",
                    expand=True,
                    padding=(1, 1)
                )
                main_content.add_row(single_panel)

            # Create the main panel containing everything
            integrated_panel = self.create_full_width_panel(
                main_content,
                title="📊 Constance Fields Summary",
                border_style="purple"
            )

            self.console.print(integrated_panel)

        except Exception as e:
            print(f"❌ ERROR in _display_constance_integrated_block: {e}")
            traceback.print_exc()
            exit(1)

    def _display_constance_details(self):
        """Display detailed Constance configuration information."""
        try:
            if not (self.config and hasattr(self.config, 'constance')):
                return

            constance_config = self.config.constance
            all_fields = constance_config.get_all_fields()

            if not all_fields:
                return

            # Show integrated summary and details in one block
            self._display_constance_integrated_block(constance_config, all_fields)

        except Exception as e:
            print(f"❌ ERROR in _display_constance_details: {e}")
            traceback.print_exc()
            exit(1)

    def _display_constance_summary(self, constance_config, all_fields):
        """Display summary of Constance fields by source."""
        try:
            # Count fields by source
            user_fields = len(constance_config.fields)  # User-defined fields
            app_fields = constance_config._get_app_constance_fields()

            # Count by app (extensions are now auto-discovered)
            tasks_count = 0
            knowbase_count = 0
            payments_count = 0

            try:
                from django_cfg.modules.base import BaseCfgModule
                base_module = BaseCfgModule()

                if base_module.is_extension_enabled("knowbase"):
                    try:
                        from extensions.apps.knowbase.config import (
                            get_django_cfg_knowbase_constance_fields,
                        )
                        knowbase_fields = get_django_cfg_knowbase_constance_fields()
                        knowbase_count = len(knowbase_fields)
                    except:
                        pass

                if base_module.is_extension_enabled("payments"):
                    try:
                        from extensions.apps.payments.config import (
                            get_django_cfg_payments_constance_fields,
                        )
                        payments_fields = get_django_cfg_payments_constance_fields()
                        payments_count = len(payments_fields)
                    except:
                        pass
            except:
                pass

            # Create summary table
            summary_table = self.create_table()
            summary_table.add_column("Source", style="cyan", width=20)
            summary_table.add_column("Fields", style="white")

            summary_table.add_row("User Defined", f"[blue]{user_fields}[/blue]")

            if tasks_count > 0:
                summary_table.add_row("Tasks Module", f"[green]{tasks_count}[/green]")
            if knowbase_count > 0:
                summary_table.add_row("Knowbase App", f"[green]{knowbase_count}[/green]")
            if payments_count > 0:
                summary_table.add_row("Payments App", f"[green]{payments_count}[/green]")

            summary_table.add_row("Total", f"[yellow]{len(all_fields)}[/yellow]")

            summary_panel = self.create_panel(
                summary_table,
                title="📊 Constance Fields Summary",
                border_style="purple"
            )

            self.console.print(summary_panel)

        except Exception as e:
            print(f"❌ ERROR in _display_constance_summary: {e}")
            traceback.print_exc()
            exit(1)

    def _display_openapi_client_info(self):
        """Display Django Client (OpenAPI) information."""
        try:
            from django_cfg.modules.django_client.core.config.service import get_openapi_service

            service = get_openapi_service()
            if not service.config or not service.config.enabled:
                return

            openapi_table = self.create_table()
            openapi_table.add_column("Setting", style="cyan", width=30)
            openapi_table.add_column("Value", style="white")

            openapi_table.add_row("📦 Status", "[green]Enabled[/green]")
            openapi_table.add_row("📊 Groups", str(len(service.config.groups)))
            openapi_table.add_row("🔗 API Prefix", f"/{service.config.api_prefix}/")
            openapi_table.add_row("📁 Output Dir", str(service.config.output_dir))

            # List groups
            group_names = [g.name for g in service.config.groups]
            if group_names:
                openapi_table.add_row("🏷️  Groups", ", ".join(group_names[:3]) + ("..." if len(group_names) > 3 else ""))

            openapi_panel = self.create_panel(
                openapi_table,
                title="🚀 Django Client (OpenAPI)",
                border_style="blue"
            )

            self.console.print(openapi_panel)
        except ImportError:
            # Django Client not available
            pass
        except Exception as e:
            print(f"❌ ERROR in _display_openapi_client_info: {e}")
            print("🔍 TRACEBACK:")
            traceback.print_exc()
            exit(1)

    def _display_commands_info(self):
        """Display management commands information."""
        try:
            from ..commands_collector import get_all_commands

            # Get command counts
            all_commands = get_all_commands()
            core_count = sum(len(commands) for commands in all_commands.get('django_cfg_core', {}).values())
            app_count = sum(len(commands) for commands in all_commands.get('django_cfg_apps', {}).values())
            project_count = sum(len(commands) for commands in all_commands.get('project_commands', {}).values())
            total_count = core_count + app_count + project_count

            # Main commands info
            commands_table = self.create_table()
            commands_table.add_column("Type", style="cyan", width=20)
            commands_table.add_column("Count", style="white")

            commands_table.add_row("🔧 Core Commands", str(core_count))
            commands_table.add_row("📱 App Commands", str(app_count))
            commands_table.add_row("🏗️ Project Commands", str(project_count))
            commands_table.add_row("📊 Total", str(total_count))

            commands_panel = self.create_full_width_panel(
                commands_table,
                title="⚡ Management Commands",
                border_style="purple"
            )

            self.console.print(commands_panel)

            # Detailed commands breakdown
            self._display_commands_breakdown()

        except Exception as e:
            print(f"❌ ERROR in _display_commands_info: {e}")
            traceback.print_exc()
            exit(1)

    def _display_commands_breakdown(self):
        """Display detailed commands breakdown."""
        try:
            from ..commands_collector import get_all_commands
            all_commands = get_all_commands()

            columns_content = []

            # Core commands
            core_commands_dict = all_commands.get('django_cfg_core', {})
            if core_commands_dict:
                core_table = self.create_table()
                core_table.add_column("Command", style="bright_blue")

                # Flatten all core commands
                all_core_commands = []
                for commands_list in core_commands_dict.values():
                    all_core_commands.extend(commands_list)

                for cmd in all_core_commands[:15]:  # Limit to first 15
                    core_table.add_row(f"• {cmd}")

                columns_content.append(self.create_panel(
                    core_table,
                    title="🔧 Core Commands",
                    border_style="blue"
                ))

            # App commands
            app_commands_dict = all_commands.get('django_cfg_apps', {})
            if app_commands_dict:
                app_table = self.create_table()
                app_table.add_column("Command", style="bright_green")

                for app_name, commands_list in app_commands_dict.items():
                    if commands_list:
                        app_table.add_row(f"[bold]{app_name.title()}:[/bold]")
                        for cmd in commands_list[:3]:  # Limit per app
                            app_table.add_row(f"  • {cmd}")

                columns_content.append(self.create_panel(
                    app_table,
                    title="📱 App Commands",
                    border_style="green"
                ))

            # Show command columns in 50/50 layout
            if len(columns_content) == 2:
                self.print_two_column_table(
                    left_content=columns_content[0].renderable,
                    right_content=columns_content[1].renderable,
                    left_title="🔧 Core Commands",
                    right_title="📱 App Commands",
                    left_style="blue",
                    right_style="green"
                )
            elif len(columns_content) == 1:
                # Single column - show as panel
                self.console.print(columns_content[0])
            elif columns_content:
                # Fallback for other cases
                self.print_columns(columns_content, equal=True, expand=True)

            # Project commands (separate panel due to length)
            project_commands_dict = all_commands.get('project_commands', {})
            if project_commands_dict:
                # Flatten all project commands
                all_project_commands = []
                for commands_list in project_commands_dict.values():
                    all_project_commands.extend(commands_list)

                # Split commands into two columns
                mid_point = len(all_project_commands) // 2
                left_commands = all_project_commands[:mid_point]
                right_commands = all_project_commands[mid_point:]

                # Create two-column table inside one panel
                project_columns_table = Table(show_header=False, box=None, padding=(0, 2))
                project_columns_table.add_column("Left", justify="left")
                project_columns_table.add_column("Right", justify="left")

                # Create content for each column
                left_content = "\n".join([f"• {cmd}" for cmd in left_commands[:15]])  # Limit to 15 per column
                right_content = "\n".join([f"• {cmd}" for cmd in right_commands[:15]])

                project_columns_table.add_row(left_content, right_content)

                project_panel = self.create_full_width_panel(
                    project_columns_table,
                    title="🏗️ Project Commands",
                    border_style="yellow"
                )

                self.console.print(project_panel)

        except Exception as e:
            print(f"❌ ERROR in _display_commands_breakdown: {e}")
            traceback.print_exc()
            exit(1)

    def _get_startup_time(self) -> str:
        """
        Get formatted startup time from timer.

        Returns:
            Formatted startup time string or None
        """
        try:
            from ..timing import get_django_startup_time
            return get_django_startup_time()
        except ImportError:
            return None

    def _display_logging_info(self):
        """Display logging paths info."""
        try:
            import os
            tmp_disabled = os.getenv('DJANGO_LOG_TO_TMP', 'true').lower() in ('false', '0', 'no')

            log_info = Text("📝 Logs → ", style="dim")
            log_info.append("./logs/", style="cyan")
            if not tmp_disabled:
                log_info.append(" | ", style="dim")
                log_info.append("/tmp/djangocfg/", style="green")
                log_info.append(" (tail -f /tmp/djangocfg/debug.log)", style="bright_blue dim")
            log_info.append(" • ", style="dim")
            log_info.append("from django_cfg.utils import get_logger", style="yellow dim")

            self.console.print(log_info)
        except Exception:
            pass

    def _display_ai_hints(self, mode: str = "short"):
        """
        Display AI development hints.

        Args:
            mode: "short" for compact view, "full" for detailed view
        """
        try:
            # Check if AI hints are enabled in config
            if self.config and hasattr(self.config, 'show_ai_hints'):
                if not self.config.show_ai_hints:
                    return

            self.ai_hints_manager.display_ai_hints(mode=mode)
        except Exception as e:
            # Don't crash on AI hints error, just skip
            pass