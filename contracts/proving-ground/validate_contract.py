from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "qortara-governance-exchange.v0.1.schema.json"
FIXTURES_DIR = ROOT / "fixtures"


def _path_text(parts: object) -> str:
    values = list(parts)
    if not values:
        return "$"
    return "$" + "".join(f"[{part!r}]" for part in values)


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    fixture_paths = sorted(FIXTURES_DIR.glob("*.json"))
    if not fixture_paths:
        print("No proving-ground fixtures found", file=sys.stderr)
        return 1

    failures: list[str] = []
    for fixture_path in fixture_paths:
        instance = json.loads(fixture_path.read_text(encoding="utf-8"))
        errors = sorted(
            validator.iter_errors(instance),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        for error in errors:
            failures.append(
                f"{fixture_path.name}:{_path_text(error.absolute_path)}: {error.message}"
            )

    if failures:
        print("Proving-ground contract validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        f"Validated {len(fixture_paths)} fixtures against {SCHEMA_PATH.name}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
