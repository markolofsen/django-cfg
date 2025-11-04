"""
Django management command for OpenAPI schema validation.

Usage:
    python manage.py validate_openapi                        # Check all serializers
    python manage.py validate_openapi --app accounts         # Check specific app
    python manage.py validate_openapi --fix                  # Auto-fix issues
    python manage.py validate_openapi --fix --dry-run        # Preview fixes
    python manage.py validate_openapi --report html          # Generate HTML report
"""

from pathlib import Path
from typing import List

from django.core.management.base import CommandError

from django_cfg.management.utils import AdminCommand


class Command(AdminCommand):
    """Validate and fix OpenAPI schema quality issues in DRF serializers."""

    command_name = 'validate_openapi'
    help = "Validate and auto-fix OpenAPI schema quality issues"

    def add_arguments(self, parser):
        """Add command arguments."""
        # Scope options
        parser.add_argument(
            "--app",
            type=str,
            help="Check specific Django app only",
        )

        parser.add_argument(
            "--file",
            type=str,
            help="Check specific file only",
        )

        parser.add_argument(
            "--pattern",
            type=str,
            default="*serializers.py",
            help="File pattern to match (default: *serializers.py)",
        )

        # Action options
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Apply auto-fixes to issues",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be fixed without applying changes",
        )

        parser.add_argument(
            "--no-confirm",
            action="store_true",
            help="Skip confirmation prompt when fixing",
        )

        # Reporting options
        parser.add_argument(
            "--report",
            type=str,
            choices=["console", "json", "html"],
            default="console",
            help="Report format (default: console)",
        )

        parser.add_argument(
            "--output",
            type=str,
            help="Output file for JSON/HTML reports",
        )

        parser.add_argument(
            "--summary",
            action="store_true",
            help="Show summary only (compact output)",
        )

        # Filtering options
        parser.add_argument(
            "--severity",
            type=str,
            choices=["error", "warning", "info"],
            help="Filter by minimum severity level",
        )

        parser.add_argument(
            "--rule",
            type=str,
            help="Check specific rule only (e.g., type-hint-001)",
        )

        parser.add_argument(
            "--fixable-only",
            action="store_true",
            help="Show only auto-fixable issues",
        )

        # Utility options
        parser.add_argument(
            "--list-rules",
            action="store_true",
            help="List available validation rules and exit",
        )

        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output",
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        try:
            # Import validation components
            from django_cfg.modules.django_client.core.validation import (
                IssueReporter,
                ValidationChecker,
            )

            # List rules
            if options["list_rules"]:
                self._list_rules()
                return

            # Get workspace directory
            workspace = self._get_workspace(options)

            # Create checker
            checker = ValidationChecker()

            # Check files
            self.stdout.write(self.style.SUCCESS("\n🔍 Scanning for issues...\n"))
            issues = self._check_files(checker, workspace, options)

            # Filter issues
            issues = self._filter_issues(issues, options)

            if not issues:
                self.stdout.write(self.style.SUCCESS("✅ No issues found!\n"))
                return

            # Report issues
            reporter = IssueReporter(use_colors=True)

            if options["summary"]:
                reporter.display_summary(issues)
            elif options["report"] == "console":
                reporter.display_console(
                    issues,
                    show_suggestions=True,
                    group_by_file=True,
                    verbose=options["verbose"]
                )
            elif options["report"] == "json":
                output_path = self._get_output_path(options, "validation_report.json")
                reporter.save_json(issues, output_path, include_stats=True)
            elif options["report"] == "html":
                output_path = self._get_output_path(options, "validation_report.html")
                reporter.save_html(issues, output_path, title="OpenAPI Validation Report")

            # Apply fixes if requested
            if options["fix"]:
                self._apply_fixes(issues, workspace, options)
            elif not options["summary"]:
                # Suggest fix command
                fixable = checker.get_fixable_issues(issues)
                if fixable:
                    self.stdout.write(
                        self.style.WARNING(
                            f"\n💡 Tip: Run with --fix to auto-fix {len(fixable)} issue(s)"
                        )
                    )

        except Exception as e:
            raise CommandError(f"Validation failed: {e}")

    def _list_rules(self):
        """List available validation rules."""
        from django_cfg.modules.django_client.core.validation import ValidationChecker

        checker = ValidationChecker()

        self.stdout.write(self.style.SUCCESS(f"\n📋 Available Validation Rules ({len(checker.rules)}):\n"))

        for rule in checker.rules:
            self.stdout.write(f"  • {rule.rule_id}: {rule.name}")
            self.stdout.write(f"    {rule.description}")
            self.stdout.write("")

    def _get_workspace(self, options) -> Path:
        """Get workspace directory to check."""
        from django.conf import settings

        if options["file"]:
            # Specific file
            file_path = Path(options["file"])
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path
            return file_path.parent

        if options["app"]:
            # Specific app
            from django.apps import apps
            try:
                app_config = apps.get_app_config(options["app"])
                return Path(app_config.path)
            except LookupError:
                raise CommandError(f"App '{options['app']}' not found")

        # Default: all apps in project
        # Try BASE_DIR first, fallback to current directory
        base_dir = getattr(settings, 'BASE_DIR', None)
        if base_dir:
            return Path(base_dir)
        else:
            return Path.cwd()

    def _check_files(self, checker, workspace: Path, options) -> List:
        """Check files for issues."""

        if options["file"]:
            # Check specific file
            file_path = Path(options["file"])
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path

            if not file_path.exists():
                raise CommandError(f"File not found: {file_path}")

            return checker.check_file(file_path)

        # Check directory
        pattern = options["pattern"]
        return checker.check_directory(workspace, pattern=pattern, recursive=True)

    def _filter_issues(self, issues: List, options) -> List:
        """Filter issues based on options."""
        from django_cfg.modules.django_client.core.validation import Severity

        filtered = issues

        # Filter by severity
        if options["severity"]:
            min_severity = Severity[options["severity"].upper()]
            severity_order = {Severity.ERROR: 3, Severity.WARNING: 2, Severity.INFO: 1}
            min_level = severity_order[min_severity]
            filtered = [
                i for i in filtered
                if severity_order[i.severity] >= min_level
            ]

        # Filter by rule
        if options["rule"]:
            filtered = [i for i in filtered if i.rule_id == options["rule"]]

        # Filter by fixability
        if options["fixable_only"]:
            filtered = [i for i in filtered if i.auto_fixable]

        return filtered

    def _get_output_path(self, options, default_name: str) -> Path:
        """Get output file path."""
        if options["output"]:
            output = Path(options["output"])
            if not output.is_absolute():
                output = Path.cwd() / output
            return output

        return Path.cwd() / default_name

    def _apply_fixes(self, issues: List, workspace: Path, options):
        """Apply fixes to issues."""
        from django_cfg.modules.django_client.core.validation import (
            SafeFixer,
            SafetyManager,
            ValidationChecker,
        )

        # Get fixable issues
        checker = ValidationChecker()
        fixable = checker.get_fixable_issues(issues)

        if not fixable:
            self.stdout.write(self.style.WARNING("\n⚠️  No auto-fixable issues found"))
            return

        # Create safety manager and fixer
        safety = SafetyManager(workspace)
        fixer = SafeFixer(safety)

        # Apply fixes
        dry_run = options["dry_run"]
        confirm = not options["no_confirm"]

        self.stdout.write(self.style.SUCCESS("\n🔧 Applying fixes...\n"))

        results = fixer.fix_issues(
            fixable,
            dry_run=dry_run,
            confirm=confirm,
            verbose=options["verbose"]
        )

        # Show results
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n🔍 Dry run completed - would fix {results['skipped']} issue(s)"
                )
            )
        else:
            if results['fixed'] > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✅ Successfully fixed {results['fixed']} issue(s)!"
                    )
                )

            if results['failed'] > 0:
                self.stdout.write(
                    self.style.ERROR(
                        f"\n❌ Failed to fix {results['failed']} issue(s)"
                    )
                )
                for error in results['errors']:
                    self.stdout.write(f"  - {error}")

            if results['skipped'] > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n⏭️  Skipped {results['skipped']} issue(s)"
                    )
                )
