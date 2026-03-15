"""DocumentationSection Pydantic model."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentationSection(BaseModel):
    """Single documentation section with title and content."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Rendered HTML content")
    file_path: Optional[Path] = Field(None, description="Source file path")
    default_open: bool = Field(False, description="Open by default")
