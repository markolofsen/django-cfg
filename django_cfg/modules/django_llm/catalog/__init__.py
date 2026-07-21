"""Model Catalog — single source of truth for model selection by role.

    from modules.django_llm.catalog import ModelRole, recommend, traits

    recommend(ModelRole.EXTRACTION)   # -> ordered model chain
    traits("qwen/qwen3.5-flash-02-23").verdict(ModelRole.EXTRACTION)  # -> Verdict.AVOID
"""

from .advisories import LLMAdvisory, check
from .fusion import DEFAULT_PRESET, DEFAULT_PRESETS, FusionCombo, default_presets
from .models import (
    DEFAULT_PROVIDER,
    PROVIDER_GONKA,
    PROVIDER_OPENAI,
    PROVIDER_OPENROUTER,
    ModelTraits,
    all_models,
    known_issues,
    provider_for,
    races,
    recommend,
    traits,
)
from .policy import ModelPlan, RequestFeatures, select_model_plan
from .roles import ModelRole, Verdict

__all__ = [
    "ModelRole",
    "Verdict",
    "ModelTraits",
    "recommend",
    "traits",
    "known_issues",
    "all_models",
    # Provider is a property of the MODEL — the catalog owns it.
    "provider_for",
    "races",
    "DEFAULT_PROVIDER",
    "PROVIDER_OPENROUTER",
    "PROVIDER_OPENAI",
    "PROVIDER_GONKA",
    "check",
    "LLMAdvisory",
    "FusionCombo",
    "DEFAULT_PRESETS",
    "DEFAULT_PRESET",
    "default_presets",
    # Pure model-selection policy (the decision layer; gateway executes it).
    "select_model_plan",
    "RequestFeatures",
    "ModelPlan",
]
