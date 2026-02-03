from __future__ import annotations

import asyncio

import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root / "apps" / "api" / "src"))

from eventcart.scripts.seed import seed  # type: ignore  # noqa: E402

if __name__ == "__main__":
    asyncio.run(seed())
