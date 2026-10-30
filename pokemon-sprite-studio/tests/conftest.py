import os

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("PSAS_ALLOW_LIVE_TESTS") == "1":
        return
    skip = pytest.mark.skip(reason="live provider test; set PSAS_ALLOW_LIVE_TESTS=1")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)
