"""
Management command to debug dashboard rendering.

Renders all dashboard sections and saves them for inspection.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.test import RequestFactory

from django_cfg.modules.django_dashboard.debug import get_debugger
from django_cfg.modules.django_dashboard.sections.commands import CommandsSection
from django_cfg.modules.django_dashboard.sections.overview import OverviewSection
from django_cfg.modules.django_dashboard.sections.stats import StatsSection
from django_cfg.modules.django_dashboard.sections.system import SystemSection


class Command(BaseCommand):
    help = "Debug dashboard rendering - saves all sections to disk"

    def add_arguments(self, parser):
        parser.add_argument(
            '--section',
            type=str,
            choices=['overview', 'stats', 'system', 'commands', 'all'],
            default='all',
            help='Which section to render (default: all)'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username to use for request (default: first superuser)'
        )

    def handle(self, *args, **options):
        # Create mock request
        factory = RequestFactory()
        request = factory.get('/admin/')

        # Get user for request
        User = get_user_model()
        username = options.get('user')

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"User '{username}' not found")
                )
                return
        else:
            # Use first superuser
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(
                    self.style.WARNING("No superuser found, using anonymous request")
                )

        if user:
            request.user = user
            self.stdout.write(f"Using user: {user.username}")

        # Get debugger
        debugger = get_debugger()
        self.stdout.write(f"Saving renders to: {debugger.output_dir}")

        section_choice = options['section']
        sections = {
            'overview': OverviewSection,
            'stats': StatsSection,
            'system': SystemSection,
            'commands': CommandsSection,
        }

        if section_choice == 'all':
            sections_to_render = sections.items()
        else:
            sections_to_render = [(section_choice, sections[section_choice])]

        # Render sections
        for name, SectionClass in sections_to_render:
            self.stdout.write(f"\nRendering {name} section...")

            try:
                section = SectionClass(request)
                html = section.render()

                # Save render
                path = debugger.save_section_render(
                    section_name=name,
                    html=html,
                    section_data=section.get_context_data() if hasattr(section, 'get_context_data') else None
                )

                self.stdout.write(
                    self.style.SUCCESS(f"✅ {name}: {len(html)} bytes, saved to {path.name}")
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ {name}: {e}")
                )
                import traceback
                traceback.print_exc()

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Done! Check renders in: {debugger.output_dir}")
        )
