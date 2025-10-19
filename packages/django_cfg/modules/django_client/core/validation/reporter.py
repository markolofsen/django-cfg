"""Issue reporter for formatting validation results."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from .rules import Issue, Severity


class IssueReporter:
    """
    Formats and displays validation issues in various formats.

    Example:
        >>> reporter = IssueReporter()
        >>> reporter.display_console(issues)
        >>> reporter.save_json(issues, Path('report.json'))
        >>> reporter.save_html(issues, Path('report.html'))
    """

    # ANSI color codes for terminal
    COLORS = {
        'reset': '\033[0m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'green': '\033[92m',
        'gray': '\033[90m',
        'bold': '\033[1m',
    }

    # Severity symbols and colors
    SEVERITY_CONFIG = {
        Severity.ERROR: {'symbol': '❌', 'color': 'red', 'label': 'ERROR'},
        Severity.WARNING: {'symbol': '⚠️ ', 'color': 'yellow', 'label': 'WARNING'},
        Severity.INFO: {'symbol': 'ℹ️ ', 'color': 'blue', 'label': 'INFO'},
    }

    def __init__(self, use_colors: bool = True):
        """
        Initialize reporter.

        Args:
            use_colors: If True, use ANSI colors in console output
        """
        self.use_colors = use_colors

    def display_console(
        self,
        issues: List[Issue],
        show_suggestions: bool = True,
        group_by_file: bool = True,
        verbose: bool = False
    ) -> None:
        """
        Display issues in console with colors and formatting.

        Args:
            issues: List of issues to display
            show_suggestions: If True, show fix suggestions
            group_by_file: If True, group issues by file
            verbose: If True, show additional context
        """
        if not issues:
            self._print("✅ No issues found!", 'green', bold=True)
            return

        # Statistics
        stats = self._get_statistics(issues)
        self._print_header(stats)

        if group_by_file:
            self._display_by_file(issues, show_suggestions, verbose)
        else:
            self._display_flat(issues, show_suggestions, verbose)

        self._print_footer(stats)

    def display_summary(self, issues: List[Issue]) -> None:
        """
        Display compact summary of issues.

        Args:
            issues: List of issues to summarize
        """
        if not issues:
            self._print("✅ No issues found!", 'green', bold=True)
            return

        stats = self._get_statistics(issues)

        print("\n📊 Validation Summary")
        print(f"   Total: {stats['total']} issue(s)")
        print(f"   Errors: {stats['by_severity']['error']} | "
              f"Warnings: {stats['by_severity']['warning']} | "
              f"Info: {stats['by_severity']['info']}")
        print(f"   Auto-fixable: {stats['fixable']} ({stats['fixable_percent']:.1f}%)")
        print(f"   Files affected: {stats['file_count']}")
        print()

    def save_json(
        self,
        issues: List[Issue],
        output_path: Path,
        include_stats: bool = True
    ) -> None:
        """
        Save issues as JSON report.

        Args:
            output_path: Path to save JSON file
            issues: List of issues
            include_stats: If True, include statistics
        """
        data = {
            'issues': [self._issue_to_dict(issue) for issue in issues]
        }

        if include_stats:
            data['statistics'] = self._get_statistics(issues)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        print(f"📄 JSON report saved to: {output_path}")

    def save_html(
        self,
        issues: List[Issue],
        output_path: Path,
        title: str = "Validation Report"
    ) -> None:
        """
        Save issues as HTML report.

        Args:
            output_path: Path to save HTML file
            issues: List of issues
            title: Report title
        """
        stats = self._get_statistics(issues)
        by_file = self._group_by_file(issues)

        html = self._generate_html(title, stats, by_file, issues)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')
        print(f"📄 HTML report saved to: {output_path}")

    # Private methods

    def _get_statistics(self, issues: List[Issue]) -> Dict[str, Any]:
        """Calculate statistics about issues."""
        by_severity = defaultdict(int)
        by_rule = defaultdict(int)
        files = set()
        fixable = 0

        for issue in issues:
            by_severity[issue.severity.value] += 1
            by_rule[issue.rule_id] += 1
            files.add(str(issue.file))
            if issue.auto_fixable:
                fixable += 1

        total = len(issues)
        fixable_percent = (fixable / total * 100) if total > 0 else 0

        return {
            'total': total,
            'fixable': fixable,
            'fixable_percent': fixable_percent,
            'file_count': len(files),
            'by_severity': {
                'error': by_severity.get('error', 0),
                'warning': by_severity.get('warning', 0),
                'info': by_severity.get('info', 0),
            },
            'by_rule': dict(by_rule),
        }

    def _group_by_file(self, issues: List[Issue]) -> Dict[Path, List[Issue]]:
        """Group issues by file path."""
        by_file = defaultdict(list)
        for issue in issues:
            by_file[issue.file].append(issue)
        return dict(by_file)

    def _print_header(self, stats: Dict[str, Any]) -> None:
        """Print report header."""
        total = stats['total']
        errors = stats['by_severity']['error']
        warnings = stats['by_severity']['warning']
        infos = stats['by_severity']['info']

        self._print("\n" + "=" * 80, 'gray')
        self._print("🔍 Validation Report", 'bold')
        self._print("=" * 80, 'gray')

        msg = f"Found {total} issue(s): "
        if errors > 0:
            msg += f"{errors} error(s), "
        if warnings > 0:
            msg += f"{warnings} warning(s), "
        if infos > 0:
            msg += f"{infos} info"

        color = 'red' if errors > 0 else 'yellow' if warnings > 0 else 'blue'
        self._print(msg, color)

        if stats['fixable'] > 0:
            self._print(
                f"✨ {stats['fixable']} issue(s) can be auto-fixed "
                f"({stats['fixable_percent']:.1f}%)",
                'green'
            )
        print()

    def _print_footer(self, stats: Dict[str, Any]) -> None:
        """Print report footer."""
        self._print("=" * 80, 'gray')
        print(f"Total: {stats['total']} issue(s) in {stats['file_count']} file(s)")
        self._print("=" * 80 + "\n", 'gray')

    def _display_by_file(
        self,
        issues: List[Issue],
        show_suggestions: bool,
        verbose: bool
    ) -> None:
        """Display issues grouped by file."""
        by_file = self._group_by_file(issues)

        for file_path, file_issues in sorted(by_file.items()):
            # File header
            self._print(f"\n📝 {file_path.name}", 'bold')
            self._print(f"   {file_path}", 'gray')

            # Issues for this file
            for issue in sorted(file_issues, key=lambda i: i.line):
                self._display_issue(issue, show_suggestions, verbose, indent=3)

    def _display_flat(
        self,
        issues: List[Issue],
        show_suggestions: bool,
        verbose: bool
    ) -> None:
        """Display issues in flat list."""
        for issue in sorted(issues, key=lambda i: (str(i.file), i.line)):
            self._display_issue(issue, show_suggestions, verbose, indent=0)

    def _display_issue(
        self,
        issue: Issue,
        show_suggestions: bool,
        verbose: bool,
        indent: int = 0
    ) -> None:
        """Display single issue."""
        prefix = " " * indent

        # Severity symbol and location
        config = self.SEVERITY_CONFIG[issue.severity]
        symbol = config['symbol']
        color = config['color']

        location = f"{issue.file.name}:{issue.line}:{issue.column}"
        self._print(f"{prefix}{symbol} {location}", color)

        # Message
        print(f"{prefix}   {issue.message}")

        # Rule ID
        if verbose:
            self._print(f"{prefix}   [{issue.rule_id}]", 'gray')

        # Suggestion
        if show_suggestions and issue.suggestion:
            auto_fix = " (auto-fixable)" if issue.auto_fixable else ""
            self._print(f"{prefix}   💡 {issue.suggestion}{auto_fix}", 'blue')

        # Context
        if verbose and issue.context:
            print(f"{prefix}   Context: {issue.context}")

        print()

    def _issue_to_dict(self, issue: Issue) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            'rule_id': issue.rule_id,
            'severity': issue.severity.value,
            'file': str(issue.file),
            'line': issue.line,
            'column': issue.column,
            'message': issue.message,
            'suggestion': issue.suggestion,
            'auto_fixable': issue.auto_fixable,
            'context': issue.context,
        }

    def _generate_html(
        self,
        title: str,
        stats: Dict[str, Any],
        by_file: Dict[Path, List[Issue]],
        all_issues: List[Issue]
    ) -> str:
        """Generate HTML report."""
        # Simple HTML template
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        h1 {{ margin: 0 0 20px 0; color: #333; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stat {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .file-section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }}
        .file-header {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}
        .issue {{
            padding: 15px;
            border-left: 4px solid;
            margin-bottom: 10px;
            background: #f8f9fa;
        }}
        .issue.error {{ border-color: #dc3545; }}
        .issue.warning {{ border-color: #ffc107; }}
        .issue.info {{ border-color: #17a2b8; }}
        .issue-location {{
            font-family: monospace;
            font-size: 13px;
            color: #666;
            margin-bottom: 5px;
        }}
        .issue-message {{
            margin-bottom: 8px;
        }}
        .issue-suggestion {{
            color: #0066cc;
            font-size: 14px;
        }}
        .auto-fixable {{
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 {title}</h1>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{stats['total']}</div>
                <div class="stat-label">Total Issues</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['by_severity']['error']}</div>
                <div class="stat-label">Errors</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['by_severity']['warning']}</div>
                <div class="stat-label">Warnings</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['fixable']}</div>
                <div class="stat-label">Auto-fixable</div>
            </div>
            <div class="stat">
                <div class="stat-value">{stats['file_count']}</div>
                <div class="stat-label">Files</div>
            </div>
        </div>
    </div>
"""

        # Group by file
        for file_path, file_issues in sorted(by_file.items()):
            html += f"""
    <div class="file-section">
        <div class="file-header">📝 {file_path.name}</div>
        <div style="color: #666; font-size: 14px; margin-bottom: 15px;">{file_path}</div>
"""

            for issue in sorted(file_issues, key=lambda i: i.line):
                severity_class = issue.severity.value
                auto_fix_badge = '<span class="auto-fixable">auto-fixable</span>' if issue.auto_fixable else ''

                html += f"""
        <div class="issue {severity_class}">
            <div class="issue-location">Line {issue.line}:{issue.column} [{issue.rule_id}]</div>
            <div class="issue-message">{issue.message} {auto_fix_badge}</div>
"""
                if issue.suggestion:
                    html += f"""
            <div class="issue-suggestion">💡 {issue.suggestion}</div>
"""
                html += """
        </div>
"""

            html += """
    </div>
"""

        html += """
</body>
</html>
"""
        return html

    def _print(self, text: str, color: str = '', bold: bool = False) -> None:
        """Print with optional color."""
        if not self.use_colors:
            print(text)
            return

        codes = []
        if bold:
            codes.append(self.COLORS['bold'])
        if color and color in self.COLORS:
            codes.append(self.COLORS[color])

        if codes:
            reset = self.COLORS['reset']
            print(f"{''.join(codes)}{text}{reset}")
        else:
            print(text)
