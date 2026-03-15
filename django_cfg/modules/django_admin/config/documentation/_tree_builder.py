"""Tree structure builder for documentation sections."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ._models import DocumentationSection


def build_tree_from_paths(
    sections: List[DocumentationSection],
    base_dir: Path,
) -> List[Dict[str, Any]]:
    """Build hierarchical tree from file paths preserving directory structure."""
    tree: Dict[str, Any] = {}

    for idx, section in enumerate(sections):
        if not section.file_path:
            tree[section.title] = {
                "id": f"section-{idx}",
                "label": section.title,
                "content": section.content,
                "is_file": True,
            }
            continue

        try:
            rel_path = section.file_path.relative_to(base_dir)
            parts = rel_path.parts
        except ValueError:
            tree[section.title] = {
                "id": f"section-{idx}",
                "label": section.title,
                "content": section.content,
                "is_file": True,
            }
            continue

        current_level = tree
        for i, part in enumerate(parts[:-1]):
            if part not in current_level:
                current_level[part] = {
                    "id": f'folder-{"-".join(parts[:i + 1])}',
                    "label": part.replace("_", " ").replace("-", " ").title(),
                    "is_file": False,
                    "children": {},
                }
            current_level = current_level[part].get("children", {})

        file_name = parts[-1]
        current_level[file_name] = {
            "id": f"section-{idx}",
            "label": section.title,
            "content": section.content,
            "is_file": True,
        }

    return dict_tree_to_list(tree)


def dict_tree_to_list(tree_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert nested dictionary tree to list format for template."""
    result = []
    for _key, node in sorted(tree_dict.items()):
        if node.get("is_file"):
            result.append({
                "id": node["id"],
                "label": node["label"],
                "content": node.get("content", ""),
                "children": [],
            })
        else:
            result.append({
                "id": node["id"],
                "label": node["label"],
                "content": None,
                "children": dict_tree_to_list(node.get("children", {})),
            })
    return result
