"""AgGrid helpers for Streamlit pages."""

from __future__ import annotations

from typing import Any


def aggrid_get_selected_row(grid_response: Any) -> dict[str, Any] | None:
    """Extract the first selected row dict from an AgGrid response.

    Handles both DataFrame (newer st-aggrid) and list (older) return formats.
    Returns None if nothing is selected.
    """
    selected_rows = grid_response.get("selected_rows")
    if selected_rows is None or len(selected_rows) == 0:
        return None
    if hasattr(selected_rows, "iloc"):
        return selected_rows.iloc[0].to_dict()
    return selected_rows[0]


def aggrid_default_builder(df: Any, *, row_height: int = 36) -> Any:
    """Return a GridOptionsBuilder pre-configured with project defaults.

    Caller must still call .configure_column() for page-specific columns,
    then .build() to get gridOptions.
    """
    from st_aggrid import GridOptionsBuilder
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, sortable=True, filter=True, min_width=80)
    gb.configure_selection("single", use_checkbox=False, pre_selected_rows=[])
    gb.configure_grid_options(rowHeight=row_height, suppressMovableColumns=True)
    return gb


def aggrid_render(
    df: Any,
    gb: Any,
    *,
    key: str,
    custom_css: dict[str, dict[str, str]] | None = None,
    height_per_row: int = 37,
    max_height: int = 500,
) -> Any:
    """Render AgGrid with project-standard settings.

    Returns the full grid_response dict.
    Height is auto-calculated: min(max_height, 60 + rows*height_per_row).
    """
    from st_aggrid import AgGrid, GridUpdateMode, DataReturnMode
    return AgGrid(
        df,
        gridOptions=gb.build(),
        height=min(max_height, 60 + len(df) * height_per_row),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        data_return_mode=DataReturnMode.AS_INPUT,
        allow_unsafe_jscode=True,
        theme="alpine",
        custom_css=custom_css or {},
        use_container_width=True,
        key=key,
    )


__all__ = [
    "aggrid_get_selected_row",
    "aggrid_default_builder",
    "aggrid_render",
]
