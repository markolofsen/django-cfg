"""
Debug utilities for dashboard rendering.

Saves rendered HTML to disk for inspection and comparison.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class DashboardDebugger:
    """Save dashboard renders for debugging."""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize debugger.

        Args:
            output_dir: Directory to save renders (default: django_cfg/debug/dashboard/)
        """
        if output_dir is None:
            # Use django_cfg package directory
            django_cfg_root = Path(__file__).parent.parent
            output_dir = django_cfg_root / 'debug' / 'dashboard'

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_render(
        self,
        html: str,
        name: str = 'dashboard',
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save rendered HTML with metadata.

        Args:
            html: Rendered HTML content
            name: Base name for files
            context: Template context data
            metadata: Additional metadata

        Returns:
            Path to saved HTML file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{name}_{timestamp}"

        # Save HTML
        html_path = self.output_dir / f"{base_name}.html"
        html_path.write_text(html, encoding='utf-8')

        # Save context as JSON
        if context:
            context_path = self.output_dir / f"{base_name}_context.json"
            # Convert context to JSON-serializable format
            serializable_context = self._make_serializable(context)
            context_path.write_text(
                json.dumps(serializable_context, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )

        # Save metadata
        meta = {
            'timestamp': timestamp,
            'name': name,
            'html_size': len(html),
            'html_lines': html.count('\n'),
        }

        if metadata:
            meta.update(metadata)

        meta_path = self.output_dir / f"{base_name}_meta.json"
        meta_path.write_text(
            json.dumps(meta, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        print(f"✅ Saved dashboard render: {html_path}")
        print(f"   Context: {context_path if context else 'N/A'}")
        print(f"   Metadata: {meta_path}")

        return html_path

    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # For non-serializable objects, use string representation
            return str(obj)

    def save_section_render(
        self,
        section_name: str,
        html: str,
        section_data: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save individual section render.

        Args:
            section_name: Name of section (overview, stats, etc.)
            html: Rendered HTML
            section_data: Section-specific data

        Returns:
            Path to saved file
        """
        return self.save_render(
            html=html,
            name=f"section_{section_name}",
            context=section_data,
            metadata={'section': section_name}
        )

    def compare_with_archive(self, current_html: str, archive_path: Path) -> Dict[str, Any]:
        """
        Compare current render with archived version.

        Args:
            current_html: Current rendered HTML
            archive_path: Path to archived HTML

        Returns:
            Comparison results
        """
        if not archive_path.exists():
            return {
                'error': f"Archive not found: {archive_path}"
            }

        archive_html = archive_path.read_text(encoding='utf-8')

        return {
            'current_size': len(current_html),
            'archive_size': len(archive_html),
            'size_diff': len(current_html) - len(archive_html),
            'current_lines': current_html.count('\n'),
            'archive_lines': archive_html.count('\n'),
            'lines_diff': current_html.count('\n') - archive_html.count('\n'),
            'identical': current_html == archive_html,
        }


# Global instance
_debugger: Optional[DashboardDebugger] = None


def get_debugger() -> DashboardDebugger:
    """Get or create global debugger instance."""
    global _debugger
    if _debugger is None:
        _debugger = DashboardDebugger()
    return _debugger


def save_dashboard_render(html: str, **kwargs) -> Path:
    """Convenience function to save dashboard render."""
    return get_debugger().save_render(html, **kwargs)


def save_section_render(section_name: str, html: str, **kwargs) -> Path:
    """Convenience function to save section render."""
    return get_debugger().save_section_render(section_name, html, **kwargs)
