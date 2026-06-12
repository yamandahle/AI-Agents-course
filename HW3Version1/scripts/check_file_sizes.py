"""Enforce max 150 lines per source file. Exit 1 if any violation found."""
from __future__ import annotations

import sys
from pathlib import Path

_MAX_LINES = 150
_SRC_ROOT = Path(__file__).parent.parent / "src"


def main() -> int:
    violations: list[tuple[Path, int]] = []
    for path in sorted(_SRC_ROOT.rglob("*.py")):
        lines = len(path.read_text(encoding="utf-8").splitlines())
        if lines > _MAX_LINES:
            violations.append((path, lines))

    if violations:
        print(f"FAIL — {len(violations)} file(s) exceed {_MAX_LINES} lines:")
        for path, count in violations:
            rel = path.relative_to(_SRC_ROOT.parent.parent)
            print(f"  {rel}  ({count} lines)")
        return 1

    print(f"OK — all files are ≤ {_MAX_LINES} lines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
