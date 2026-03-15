"""Data table component for Streamlit admin."""

from typing import Any

import streamlit as st
from pydantic import BaseModel

# Try to import streamlit-aggrid, fallback to native dataframe
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    HAS_AGGRID = True
except ImportError:
    HAS_AGGRID = False


def render_data_table(
    data: list[BaseModel],
    selection: bool = False,
    pagination: bool = True,
    page_size: int = 10,
) -> list[dict[str, Any]] | None:
    """Render data table with optional selection.

    Args:
        data: List of Pydantic models to display.
        selection: Enable row selection (default: False).
        pagination: Enable pagination (default: True).
        page_size: Rows per page (default: 10).

    Returns:
        Selected rows as list of dicts if selection enabled, else None.
    """
    if not data:
        st.info("No data available")
        return None

    if HAS_AGGRID:
        return _render_aggrid_table(data, selection, pagination, page_size)
    return _render_fallback_table(data, selection)


def _render_aggrid_table(
    data: list[BaseModel],
    selection: bool,
    pagination: bool,
    page_size: int,
) -> list[dict[str, Any]] | None:
    """Render table using AG Grid."""
    import pandas as pd

    df = pd.DataFrame([item.model_dump() for item in data])

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filterable=True, sortable=True, resizable=True)

    if selection:
        gb.configure_selection("multiple", use_checkbox=True)

    if pagination:
        gb.configure_pagination(
            paginationAutoPageSize=False, paginationPageSize=page_size
        )

    update_mode = (
        GridUpdateMode.SELECTION_CHANGED if selection else GridUpdateMode.NO_UPDATE
    )

    response = AgGrid(
        df,
        gridOptions=gb.build(),
        theme="streamlit",
        fit_columns_on_grid_load=True,
        update_mode=update_mode,
    )

    if selection and response.selected_rows is not None:
        return response.selected_rows.to_dict("records")
    return None


def _render_fallback_table(
    data: list[BaseModel],
    selection: bool,
) -> list[dict[str, Any]] | None:
    """Render simple fallback table using native Streamlit."""
    import pandas as pd

    df = pd.DataFrame([item.model_dump() for item in data])
    st.dataframe(df, use_container_width=True, hide_index=True)

    if selection:
        st.caption("Row selection requires streamlit-aggrid package")
    return None
