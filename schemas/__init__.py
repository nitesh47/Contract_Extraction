
from importlib import import_module
from pathlib import Path
from typing import Dict, Type

from .generic import GenericContractSchema

_current_dir = Path(__file__).parent
for p in _current_dir.glob("*.py"):
    if p.name not in {"__init__.py", "generic.py"}:
        import_module(f"{__name__}.{p.stem}")
