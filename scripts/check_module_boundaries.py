#!/usr/bin/env python3
"""
M6 — module-boundary lint rule for the monolith (app/).

Rule (per target_architecture.md §2): a module may import another module's
api-layer/main entrypoint (the equivalent of "calling its public HTTP
contract"), but never reach directly into another module's domain,
application, or infrastructure internals (its ORM models, repositories,
use-cases). `app.core` and `app.main` are shared/entrypoint, not modules,
and are always allowed.

Exit code 0 = no violations, 1 = violations found (prints each one).
Run from the repo root: python3 scripts/check_module_boundaries.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

MODULES = {
    "identity", "farm", "poultry", "inventory",
    "finance", "notifications", "reporting", "gateway",
}
ALWAYS_ALLOWED = {"core", "main"}

IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+app\.([a-zA-Z_]+)(?:\.([a-zA-Z_]+))?")


def check_file(path: Path, owning_module: str) -> list[str]:
    violations = []
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        m = IMPORT_RE.match(line)
        if not m:
            continue
        target_module, target_submodule = m.group(1), m.group(2)
        if target_module == owning_module or target_module in ALWAYS_ALLOWED:
            continue
        if target_module not in MODULES:
            continue
        # Allowed: importing another module's top-level package/main entrypoint only.
        if target_submodule in (None, "main"):
            continue
        violations.append(
            f"{path}:{lineno}: {owning_module} reaches into app.{target_module}.{target_submodule} "
            f"(internals) — only app.{target_module} or app.{target_module}.main is allowed"
        )
    return violations


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    app_dir = repo_root / "app"
    violations: list[str] = []
    for module in sorted(MODULES):
        module_dir = app_dir / module
        if not module_dir.is_dir():
            continue
        for py_file in module_dir.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            violations.extend(check_file(py_file, module))

    if violations:
        print(f"Module boundary violations found ({len(violations)}):")
        for v in violations:
            print(f"  {v}")
        return 1

    print("No module boundary violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
