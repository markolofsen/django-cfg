"""Ready-made task methods: name the JOB, never the model.

    from django_cfg.modules.django_llm import tasks

    car = tasks.extract(Car, listing_text)               # TaskResult(value, model, usage)
    label = tasks.classify(text, labels=["sale", "rent"])
    ru = tasks.translate("Sunroof", target="ru", domain="used car listings")
    vec = tasks.embed("some text")
    text = await tasks.aocr(png_bytes, "image/png")
    verdict = tasks.judge("Ocean Club Estates", ["Ocean Club Residences", "Ocean Club Estates II"])
    answer = tasks.chat([{"role": "user", "content": "hi"}])

Every method resolves its ordered model chain from ONE table
(``catalog/tasks.py``: ``get_task_models(task)``), overridable per project via
``settings.DJANGO_LLM_TASKS`` (see ``@docs/task-methods.md``), walks the chain on
failure and reports the model that answered in ``result.model``.

``TaskResult`` unpacks like the older presets: ``value, model, usage = tasks.extract(...)``.
"""

from ..catalog.tasks import (
    TASKS,
    TaskSpec,
    get_task_models,
    get_task_spec,
    reset_task_overrides,
    set_task_models,
)
from .methods import (
    JudgeVerdict,
    TaskResult,
    achat,
    aclassify,
    aembed,
    aescalate,
    aextract,
    ajudge,
    aocr,
    atranscribe,
    atranslate,
    chat,
    classify,
    embed,
    escalate,
    extract,
    judge,
    ocr,
    transcribe,
    translate,
)

__all__ = [
    "JudgeVerdict", "TASKS", "TaskResult", "TaskSpec",
    "achat", "aclassify", "aembed", "aescalate", "aextract", "ajudge", "aocr", "atranscribe", "atranslate",
    "chat", "classify", "embed", "escalate", "extract", "judge", "ocr", "transcribe", "translate",
    "get_task_models", "get_task_spec", "reset_task_overrides", "set_task_models",
]
