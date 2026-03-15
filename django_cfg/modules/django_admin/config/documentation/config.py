"""DocumentationConfig Pydantic model."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ._loader import get_section_title, resolve_path, scan_markdown_files
from ._mgmt_discovery import discover_management_commands
from ._models import DocumentationSection
from ._tree_builder import build_tree_from_paths, dict_tree_to_list


class DocumentationConfig(BaseModel):
    """
    Configuration for markdown documentation in Django Admin.

    Supports three modes:
    1. Directory mode: DocumentationConfig(source_dir="docs", title="Docs")
    2. Single file mode: DocumentationConfig(source_file="docs/README.md", title="Docs")
    3. String content mode: DocumentationConfig(source_content="# Hello", title="Docs")
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    source_dir: Optional[Union[str, Path]] = Field(
        None, description="Path to directory with .md files (scans recursively)"
    )
    source_file: Optional[Union[str, Path]] = Field(
        None, description="Path to single markdown file"
    )
    source_content: Optional[str] = Field(
        None, description="Markdown content as string"
    )

    title: str = Field("Documentation", description="Main title for documentation block")
    show_on_changelist: bool = Field(True, description="Show on list page (above table)")
    show_on_changeform: bool = Field(True, description="Show on edit/add page (before fieldsets)")
    enable_plugins: bool = Field(True, description="Enable mistune plugins")
    sort_sections: bool = Field(True, description="Sort sections alphabetically by title")
    show_management_commands: bool = Field(
        True, description="Auto-discover and display management commands from app"
    )
    default_open: bool = Field(False, description="Open sections by default")

    @field_validator("source_dir", "source_file", "source_content")
    @classmethod
    def validate_source(cls, v, info):
        return v

    def get_sections(self, app_path: Optional[Path] = None) -> List[DocumentationSection]:
        """Get all documentation sections based on configured source mode."""
        from django_cfg.modules.django_admin.utils import MarkdownRenderer

        sections: List[DocumentationSection] = []

        if self.source_dir:
            resolved_dir = resolve_path(self.source_dir, app_path)
            if resolved_dir and resolved_dir.is_dir():
                for idx, md_file in enumerate(scan_markdown_files(resolved_dir)):
                    try:
                        content = md_file.read_text(encoding="utf-8")
                        rendered = MarkdownRenderer.render_markdown(content, enable_plugins=self.enable_plugins)
                        sections.append(DocumentationSection(
                            title=get_section_title(md_file, resolved_dir),
                            content=rendered,
                            file_path=md_file,
                            default_open=(idx == 0 and self.default_open),
                        ))
                    except Exception:
                        continue

        elif self.source_file:
            resolved_file = resolve_path(self.source_file, app_path)
            if resolved_file and resolved_file.is_file():
                try:
                    content = resolved_file.read_text(encoding="utf-8")
                    rendered = MarkdownRenderer.render_markdown(content, enable_plugins=self.enable_plugins)
                    sections.append(DocumentationSection(
                        title=get_section_title(resolved_file, resolved_file.parent),
                        content=rendered,
                        file_path=resolved_file,
                        default_open=self.default_open,
                    ))
                except Exception:
                    pass

        elif self.source_content:
            rendered = MarkdownRenderer.render_markdown(self.source_content, enable_plugins=self.enable_plugins)
            sections.append(DocumentationSection(
                title=self.title,
                content=rendered,
                default_open=self.default_open,
            ))

        if self.sort_sections and len(sections) > 1:
            sections.sort(key=lambda s: s.title.lower())

        return sections

    def get_tree_structure(self, app_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Build hierarchical tree structure for modal sidebar navigation."""
        sections = self.get_sections(app_path)
        if not sections:
            return []

        if self.source_dir:
            resolved_dir = resolve_path(self.source_dir, app_path)
            if resolved_dir and resolved_dir.is_dir():
                return build_tree_from_paths(sections, resolved_dir)

        return [
            {"id": f"section-{idx}", "label": s.title, "content": s.content, "children": []}
            for idx, s in enumerate(sections)
        ]

    def get_content(self, app_path: Optional[Path] = None) -> Optional[str]:
        """Get rendered markdown content (legacy single-section method)."""
        sections = self.get_sections(app_path)
        return sections[0].content if sections else None
