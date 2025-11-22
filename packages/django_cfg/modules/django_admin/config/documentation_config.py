"""
Documentation configuration for Django Admin.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentationSection(BaseModel):
    """Single documentation section with title and content."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Rendered HTML content")
    file_path: Optional[Path] = Field(None, description="Source file path")
    default_open: bool = Field(False, description="Open by default")


class DocumentationConfig(BaseModel):
    """
    Configuration for markdown documentation in Django Admin.

    Displays documentation in a modal window with tree navigation (left sidebar)
    and rendered content (right panel).

    Supports three modes:

    1. **Directory mode** (recommended):
       Automatically discovers all .md files in directory recursively.
       Each file becomes a tree item in modal sidebar.

       DocumentationConfig(
           source_dir="docs",  # Relative to app
           title="Documentation"
       )

    2. **Single file mode**:
       Displays single markdown file.

       DocumentationConfig(
           source_file="docs/README.md",
           title="Documentation"
       )

    3. **String content mode**:
       Direct markdown content.

       DocumentationConfig(
           source_content="# Hello\\nWorld",
           title="Documentation"
       )

    Path resolution:
    - Relative: "docs" → current app's docs/
    - Project: "apps/crypto/docs" → project root
    - Absolute: "/full/path/to/docs"
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Content source (one of these must be provided)
    source_dir: Optional[Union[str, Path]] = Field(
        None,
        description="Path to directory with .md files (scans recursively)"
    )
    source_file: Optional[Union[str, Path]] = Field(
        None,
        description="Path to single markdown file"
    )
    source_content: Optional[str] = Field(
        None,
        description="Markdown content as string"
    )

    # Display options
    title: str = Field("Documentation", description="Main title for documentation block")

    # Placement
    show_on_changelist: bool = Field(True, description="Show on list page (above table)")
    show_on_changeform: bool = Field(True, description="Show on edit/add page (before fieldsets)")

    # Markdown rendering
    enable_plugins: bool = Field(True, description="Enable mistune plugins")

    # Sorting
    sort_sections: bool = Field(True, description="Sort sections alphabetically by title")

    # Management commands discovery
    show_management_commands: bool = Field(
        True,
        description="Auto-discover and display management commands from app"
    )

    @field_validator('source_dir', 'source_file', 'source_content')
    @classmethod
    def validate_source(cls, v, info):
        """Ensure at least one source is provided."""
        return v

    def _resolve_path(self, path: Union[str, Path], app_path: Optional[Path] = None) -> Optional[Path]:
        """
        Resolve file or directory path with support for:
        - Relative to app: "docs"
        - Relative to project: "apps/myapp/docs"
        - Absolute: "/full/path/to/docs"

        Args:
            path: Path to resolve
            app_path: Path to the app directory (auto-detected from model)

        Returns:
            Resolved absolute path or None
        """
        if not path:
            return None

        path_obj = Path(path)

        # If absolute path, return as is
        if path_obj.is_absolute():
            return path_obj if path_obj.exists() else None

        # Try project root first (for paths like "apps/crypto/docs")
        from django.conf import settings
        base_dir = Path(settings.BASE_DIR)

        # Try relative to project root
        project_path = base_dir / path_obj
        if project_path.exists():
            return project_path

        # Try relative to app if provided
        if app_path:
            app_path_resolved = app_path / path_obj
            if app_path_resolved.exists():
                return app_path_resolved

        # Try to find in any app's directory
        if hasattr(settings, 'INSTALLED_APPS'):
            for app in settings.INSTALLED_APPS:
                try:
                    # Get app module
                    import importlib
                    app_module = importlib.import_module(app.split('.')[0])
                    if hasattr(app_module, '__path__'):
                        app_dir = Path(app_module.__path__[0])
                        app_file = app_dir / path_obj
                        if app_file.exists():
                            return app_file
                except (ImportError, AttributeError, IndexError):
                    continue

        return None

    def _scan_markdown_files(self, directory: Path) -> List[Path]:
        """
        Recursively scan directory for markdown files.

        Args:
            directory: Directory to scan

        Returns:
            List of markdown file paths
        """
        md_files = []

        if not directory.is_dir():
            return md_files

        # Recursively find all .md files
        for md_file in directory.rglob("*.md"):
            if md_file.is_file():
                md_files.append(md_file)

        return md_files

    def _get_section_title(self, file_path: Path, base_dir: Path) -> str:
        """
        Generate section title from file path.

        Strategies:
        1. Extract first H1 from content if available
        2. If README.md → use parent directory name
        3. If nested → use "Parent / Filename"

        Args:
            file_path: Path to markdown file
            base_dir: Base documentation directory

        Returns:
            Section title
        """
        # Try to extract H1 from file
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()
        except Exception:
            pass

        # Fallback to filename
        relative_path = file_path.relative_to(base_dir)

        # If README.md, use parent directory name
        if file_path.stem.lower() == 'readme':
            if relative_path.parent != Path('.'):
                return str(relative_path.parent).replace('/', ' / ').replace('_', ' ').title()
            return "Overview"

        # Build title from path
        parts = []
        if relative_path.parent != Path('.'):
            parts.append(str(relative_path.parent).replace('/', ' / ').replace('_', ' ').title())

        # Add filename without extension
        parts.append(file_path.stem.replace('_', ' ').replace('-', ' ').title())

        return ' / '.join(parts)

    def get_sections(self, app_path: Optional[Path] = None) -> List[DocumentationSection]:
        """
        Get all documentation sections.

        Returns list of sections based on mode:
        - Directory mode: One section per .md file
        - Single file mode: One section
        - String content mode: One section

        Args:
            app_path: Optional path to app directory for relative path resolution

        Returns:
            List of DocumentationSection objects
        """
        from django_cfg.modules.django_admin.utils import MarkdownRenderer

        sections = []

        # Directory mode
        if self.source_dir:
            resolved_dir = self._resolve_path(self.source_dir, app_path)
            if resolved_dir and resolved_dir.is_dir():
                md_files = self._scan_markdown_files(resolved_dir)

                for idx, md_file in enumerate(md_files):
                    try:
                        content = md_file.read_text(encoding='utf-8')
                        rendered = MarkdownRenderer.render_markdown(
                            content,
                            enable_plugins=self.enable_plugins
                        )

                        title = self._get_section_title(md_file, resolved_dir)

                        sections.append(DocumentationSection(
                            title=title,
                            content=rendered,
                            file_path=md_file,
                            default_open=(idx == 0 and self.default_open)
                        ))
                    except Exception as e:
                        # Skip files that can't be read
                        continue

        # Single file mode
        elif self.source_file:
            resolved_file = self._resolve_path(self.source_file, app_path)
            if resolved_file and resolved_file.is_file():
                try:
                    content = resolved_file.read_text(encoding='utf-8')
                    rendered = MarkdownRenderer.render_markdown(
                        content,
                        enable_plugins=self.enable_plugins
                    )

                    title = self._get_section_title(resolved_file, resolved_file.parent)

                    sections.append(DocumentationSection(
                        title=title,
                        content=rendered,
                        file_path=resolved_file,
                        default_open=self.default_open
                    ))
                except Exception:
                    pass

        # String content mode
        elif self.source_content:
            rendered = MarkdownRenderer.render_markdown(
                self.source_content,
                enable_plugins=self.enable_plugins
            )

            sections.append(DocumentationSection(
                title=self.title,
                content=rendered,
                default_open=self.default_open
            ))

        # Sort sections if requested
        if self.sort_sections and len(sections) > 1:
            sections.sort(key=lambda s: s.title.lower())

        return sections

    def _discover_management_commands(self, app_path: Optional[Path] = None) -> List[Dict[str, any]]:
        """
        Discover management commands in app's management/commands directory.

        Args:
            app_path: Path to the app directory

        Returns:
            List of command dictionaries with name, help text, and arguments
        """
        commands = []

        if not app_path:
            return commands

        commands_dir = app_path / "management" / "commands"
        if not commands_dir.exists() or not commands_dir.is_dir():
            return commands

        # Find all command files
        for cmd_file in commands_dir.glob("*.py"):
            if cmd_file.stem.startswith('_'):
                continue

            try:
                # Import the command module
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    f"command_{cmd_file.stem}", cmd_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Get the Command class
                    if hasattr(module, 'Command'):
                        cmd_class = module.Command
                        cmd_instance = cmd_class()

                        # Extract command info
                        command_info = {
                            'name': cmd_file.stem,
                            'help': getattr(cmd_instance, 'help', 'No description available'),
                            'arguments': []
                        }

                        # Try to extract arguments if add_arguments method exists
                        if hasattr(cmd_instance, 'add_arguments'):
                            # Create a mock parser to extract arguments
                            import argparse
                            parser = argparse.ArgumentParser()
                            try:
                                cmd_instance.add_arguments(parser)
                                # Extract arguments from parser
                                for action in parser._actions:
                                    if action.dest != 'help':
                                        arg_info = {
                                            'name': '/'.join(action.option_strings) if action.option_strings else action.dest,
                                            'help': action.help or '',
                                            'required': action.required if hasattr(action, 'required') else False,
                                            'default': action.default if action.default != argparse.SUPPRESS else None
                                        }
                                        command_info['arguments'].append(arg_info)
                            except Exception:
                                pass

                        commands.append(command_info)

            except Exception:
                # Skip commands that can't be imported
                continue

        # Sort commands alphabetically
        commands.sort(key=lambda c: c['name'])

        return commands

    def get_tree_structure(self, app_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Build hierarchical tree structure from documentation sections.

        For modal view with sidebar navigation. Groups sections by directory path.

        Args:
            app_path: Optional path to app directory for relative path resolution

        Returns:
            List of tree nodes with 'label', 'id', 'content', and optional 'children'
        """
        sections = self.get_sections(app_path)

        if not sections:
            return []

        # If source_dir mode, build hierarchy from file paths
        if self.source_dir:
            resolved_dir = self._resolve_path(self.source_dir, app_path)
            if resolved_dir and resolved_dir.is_dir():
                return self._build_tree_from_paths(sections, resolved_dir)

        # Flat list for single file or string content mode
        return [
            {
                'id': f'section-{idx}',
                'label': section.title,
                'content': section.content,
                'children': []
            }
            for idx, section in enumerate(sections)
        ]

    def _build_tree_from_paths(
        self,
        sections: List[DocumentationSection],
        base_dir: Path
    ) -> List[Dict[str, Any]]:
        """
        Build hierarchical tree from file paths preserving directory structure.

        Args:
            sections: List of documentation sections with file_path
            base_dir: Base directory for relative path calculation

        Returns:
            Tree structure as nested dictionaries
        """
        tree: Dict[str, Any] = {}

        for idx, section in enumerate(sections):
            if not section.file_path:
                # Fallback for sections without file path
                tree[section.title] = {
                    'id': f'section-{idx}',
                    'label': section.title,
                    'content': section.content,
                    'is_file': True
                }
                continue

            # Get relative path parts
            try:
                rel_path = section.file_path.relative_to(base_dir)
                parts = rel_path.parts
            except ValueError:
                # File outside base_dir, use title
                tree[section.title] = {
                    'id': f'section-{idx}',
                    'label': section.title,
                    'content': section.content,
                    'is_file': True
                }
                continue

            # Navigate/create tree structure
            current_level = tree
            for i, part in enumerate(parts[:-1]):  # All but last (file)
                if part not in current_level:
                    current_level[part] = {
                        'id': f'folder-{"-".join(parts[:i+1])}',
                        'label': part.replace('_', ' ').replace('-', ' ').title(),
                        'is_file': False,
                        'children': {}
                    }
                current_level = current_level[part].get('children', {})

            # Add file node
            file_name = parts[-1]
            current_level[file_name] = {
                'id': f'section-{idx}',
                'label': section.title,
                'content': section.content,
                'is_file': True
            }

        # Convert nested dict to list format
        return self._dict_tree_to_list(tree)

    def _dict_tree_to_list(self, tree_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert nested dictionary tree to list format for template."""
        result = []

        for key, node in sorted(tree_dict.items()):
            if node.get('is_file'):
                result.append({
                    'id': node['id'],
                    'label': node['label'],
                    'content': node.get('content', ''),
                    'children': []
                })
            else:
                # Folder node
                children = self._dict_tree_to_list(node.get('children', {}))
                result.append({
                    'id': node['id'],
                    'label': node['label'],
                    'content': None,  # Folders don't have content
                    'children': children
                })

        return result

    def get_content(self, app_path: Optional[Path] = None) -> Optional[str]:
        """
        Get rendered markdown content (legacy single-section method).

        For multi-section support, use get_sections() instead.

        Args:
            app_path: Optional path to app directory for relative path resolution

        Returns:
            Rendered HTML string or None
        """
        sections = self.get_sections(app_path)
        if sections:
            return sections[0].content
        return None
