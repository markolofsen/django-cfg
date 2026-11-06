"""pytest plugin for hosts of the chat harness: the `live` marker.

    # conftest.py
    pytest_plugins = ["django_cfg.modules.django_llm.agent.chat.pytest_plugin"]

`@pytest.mark.live` tests call a real model and cost money. They are deselected by default (as if `-m "not live"` were
set) and skipped unless `ASSISTANT_LIVE=1` and a model key exist. Passing your own `-m` expression turns the default off.
"""

from __future__ import annotations

import pytest

from django_cfg.modules.django_llm.agent.chat.testing import live_blocker


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "live: calls a real model and costs money; skipped unless ASSISTANT_LIVE=1 and a model key exist")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    live = [i for i in items if i.get_closest_marker("live")]
    if not live:
        return
    if not config.getoption("markexpr", default=""):
        config.hook.pytest_deselected(items=live)
        items[:] = [i for i in items if i not in live]
        return
    reason = live_blocker()
    if reason:
        skip = pytest.mark.skip(reason=reason)
        for item in live:
            item.add_marker(skip)
