import sys
import os
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SVC_PATH = os.path.join(ROOT, "services", "reporting-service")


@pytest.fixture(scope="module", autouse=True)
def _use_reporting():
    """Switch sys.path to reporting-service before this module's tests run."""
    for k in [k for k in list(sys.modules) if k.startswith(("app", "shared"))]:
        del sys.modules[k]
    for p in list(sys.path):
        if os.sep + "services" + os.sep in p or "/services/" in p:
            sys.path.remove(p)
    if SVC_PATH not in sys.path:
        sys.path.insert(0, SVC_PATH)
    yield
