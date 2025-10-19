"""
Swagger UI settings for DRF Spectacular.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field


class SwaggerUISettings(BaseModel):
    """Swagger UI specific settings."""

    try_it_out_enabled: bool = Field(
        default=True, description="Enable Try It Out feature"
    )
    doc_expansion: str = Field(
        default="list", description="Default expansion setting (list, full, none)"
    )
    deep_linking: bool = Field(default=True, description="Enable deep linking")
    persist_authorization: bool = Field(
        default=True, description="Persist authorization data"
    )
    display_operation_id: bool = Field(
        default=True, description="Display operation IDs"
    )
    default_models_expand_depth: int = Field(
        default=1, description="Default expansion depth for models"
    )
    default_model_expand_depth: int = Field(
        default=1, description="Default expansion depth for model"
    )
    default_model_rendering: str = Field(
        default="model", description="Default model rendering"
    )
    filter: bool = Field(default=True, description="Enable filtering")
    show_extensions: bool = Field(default=False, description="Show extensions")
    show_common_extensions: bool = Field(
        default=True, description="Show common extensions"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Swagger UI."""
        return {
            "tryItOutEnabled": self.try_it_out_enabled,
            "docExpansion": self.doc_expansion,
            "deepLinking": self.deep_linking,
            "persistAuthorization": self.persist_authorization,
            "displayOperationId": self.display_operation_id,
            "defaultModelsExpandDepth": self.default_models_expand_depth,
            "defaultModelExpandDepth": self.default_model_expand_depth,
            "defaultModelRendering": self.default_model_rendering,
            "filter": self.filter,
            "showExtensions": self.show_extensions,
            "showCommonExtensions": self.show_common_extensions,
        }


__all__ = [
    "SwaggerUISettings",
]
