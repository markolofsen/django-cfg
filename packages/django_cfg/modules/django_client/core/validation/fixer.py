"""Safe auto-fixer with rollback support."""

from typing import Any, Dict, List

from .rules import Issue
from .rules.type_hints import TypeHintRule
from .safety import SafetyManager


class SafeFixer:
    """
    Safely apply fixes to code with backup/rollback.

    Example:
        >>> safety = SafetyManager(workspace=Path('.'))
        >>> fixer = SafeFixer(safety)
        >>> results = fixer.fix_issues(issues, dry_run=False)
        >>> print(f"Fixed: {results['fixed']}")
    """

    def __init__(self, safety_manager: SafetyManager):
        """
        Initialize fixer.

        Args:
            safety_manager: SafetyManager instance for backups/rollbacks
        """
        self.safety = safety_manager
        self.rules = {
            'type-hint-001': TypeHintRule(),
            # Future rules here
        }

    def fix_issues(
        self,
        issues: List[Issue],
        dry_run: bool = True,
        confirm: bool = True,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Fix issues with safety guarantees.

        Args:
            issues: List of issues to fix
            dry_run: If True, only show what would be fixed
            confirm: If True, ask for user confirmation
            verbose: If True, show detailed progress

        Returns:
            Dict with results: {
                'fixed': int,
                'failed': int,
                'skipped': int,
                'errors': List[str]
            }
        """
        results = {
            'fixed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

        # Filter auto-fixable issues
        fixable_issues = [i for i in issues if self._can_fix(i)]

        if not fixable_issues:
            if verbose:
                print("ℹ️  No auto-fixable issues found")
            return results

        # Dry run: just show what would be fixed
        if dry_run:
            print(f"\n🔍 Dry run: {len(fixable_issues)} issue(s) can be fixed\n")
            for issue in fixable_issues:
                print(f"  {issue.file.name}:{issue.line}")
                print(f"    {issue.message}")
                print(f"    Fix: {issue.suggestion}\n")
            results['skipped'] = len(fixable_issues)
            return results

        # Ask for confirmation
        if confirm:
            if not self._confirm_fixes(fixable_issues):
                results['skipped'] = len(fixable_issues)
                return results

        # Start transaction
        transaction_id = self.safety.start_transaction()
        print(f"\n🔧 Starting fixes (transaction: {transaction_id})\n")

        try:
            # Group by file
            by_file = {}
            for issue in fixable_issues:
                by_file.setdefault(issue.file, []).append(issue)

            # Fix each file
            for file_path, file_issues in by_file.items():
                if verbose:
                    print(f"📝 Fixing {file_path.name} ({len(file_issues)} issue(s))...")

                # Backup
                self.safety.backup_file(file_path)

                # Group issues by rule_id for batch processing
                issues_by_rule = {}
                for issue in file_issues:
                    issues_by_rule.setdefault(issue.rule_id, []).append(issue)

                # Apply fixes by rule
                file_success = 0
                for rule_id, rule_issues in issues_by_rule.items():
                    rule = self.rules.get(rule_id)
                    if not rule:
                        results['failed'] += len(rule_issues)
                        continue

                    # Use batch fix if available (for better handling of imports)
                    if hasattr(rule, 'fix_batch') and len(rule_issues) > 1:
                        try:
                            if rule.fix_batch(rule_issues):
                                file_success += len(rule_issues)
                                if verbose:
                                    for issue in rule_issues:
                                        print(f"    ✓ {issue.message}")
                            else:
                                results['failed'] += len(rule_issues)
                        except Exception as e:
                            if verbose:
                                print(f"    ✗ Batch fix failed: {e}")
                            results['failed'] += len(rule_issues)
                    else:
                        # Fall back to individual fixes
                        for issue in rule_issues:
                            if self._fix_issue(issue, verbose):
                                file_success += 1
                            else:
                                results['failed'] += 1

                # Validate syntax
                if file_success > 0:
                    if self.safety.validate_syntax(file_path):
                        results['fixed'] += file_success
                        if verbose:
                            print(f"  ✅ Fixed {file_success} issue(s)")
                    else:
                        # Rollback this file
                        self.safety.rollback_file(file_path)
                        results['failed'] += file_success
                        results['errors'].append(f"Syntax error after fixing {file_path.name}")
                        print(f"  ❌ Syntax error - rolled back {file_path.name}")

            # Commit if successful
            if results['failed'] == 0:
                self.safety.commit_transaction()
                print(f"\n✅ Successfully fixed {results['fixed']} issue(s)")
            else:
                self.safety.rollback_transaction()
                print(f"\n⚠️  Rolled back due to {results['failed']} failure(s)")

        except Exception as e:
            # Rollback on any error
            self.safety.rollback_transaction()
            results['errors'].append(str(e))
            print(f"\n❌ Error: {e}")
            print("   Rolled back all changes")

        return results

    def _can_fix(self, issue: Issue) -> bool:
        """Check if issue can be auto-fixed."""
        rule = self.rules.get(issue.rule_id)
        return rule and rule.can_fix(issue)

    def _fix_issue(self, issue: Issue, verbose: bool = False) -> bool:
        """Fix a single issue."""
        rule = self.rules.get(issue.rule_id)
        if not rule:
            return False

        try:
            success = rule.fix(issue)
            if verbose and success:
                print(f"    ✓ {issue.message}")
            return success
        except Exception as e:
            if verbose:
                print(f"    ✗ {issue.message}: {e}")
            return False

    def _confirm_fixes(self, issues: List[Issue]) -> bool:
        """Ask user to confirm fixes."""
        print(f"\n🔧 Ready to fix {len(issues)} issue(s):\n")

        # Group by file
        by_file = {}
        for issue in issues:
            by_file.setdefault(issue.file, []).append(issue)

        # Show summary
        for file_path, file_issues in list(by_file.items())[:5]:
            print(f"  📝 {file_path.name}: {len(file_issues)} issue(s)")
            for issue in file_issues[:2]:
                print(f"     - {issue.message}")
            if len(file_issues) > 2:
                print(f"     ... and {len(file_issues) - 2} more")

        if len(by_file) > 5:
            print(f"  ... and {len(by_file) - 5} more file(s)")

        print()
        response = input("Apply these fixes? [y/N]: ")
        return response.lower() in ['y', 'yes']
