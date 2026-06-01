"""Model Catalog — single source of truth for model selection by role.

    from django_cfg.modules.django_llm.catalog import ModelRole, recommend, traits

    recommend(ModelRole.EXTRACTION)   # -> ordered model chain
    traits("qwen/qwen3.5-flash-02-23").verdict(ModelRole.EXTRACTION)  # -> Verdict.AVOID

See ``@dev/v2/PLAN.md`` for the design and the knowledge sources.
"""

from .advisories import LLMAdvisory, check
from .models import ModelTraits, all_models, known_issues, recommend, traits
from .roles import ModelRole, Verdict

__all__ = [
    "ModelRole",
    "Verdict",
    "ModelTraits",
    "recommend",
    "traits",
    "known_issues",
    "all_models",
    "check",
    "LLMAdvisory",
]
