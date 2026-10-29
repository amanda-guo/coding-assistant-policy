#!/usr/bin/env python3
"""Validate a coding assistant policy file.

Two layers:
  1. Structure: JSON Schema (schema/policy.schema.json)
  2. Rules: org guardrails the schema can't express (checked below)

Exit code 0 = valid, 1 = invalid, 2 = could not read input.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# Every enabled assistant must exclude at least these paths.
REQUIRED_EXCLUSIONS = {"**/.env*", "**/secrets/**"}


def validate_schema(policy: dict, schema: dict) -> list[str]:
    from jsonschema import Draft202012Validator  # imported here so rules are testable without it

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(policy), key=lambda e: list(map(str, e.absolute_path)))
    return [
        f"schema: {'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
        for e in errors
    ]


def validate_rules(policy: dict) -> list[str]:
    errors = []
    for name, cfg in policy["assistants"].items():
        models = cfg["models"]
        if models["default"] not in models["allowed"]:
            errors.append(
                f"rule: {name}: default model '{models['default']}' is not in the allowed list"
            )

        if cfg["enabled"]:
            missing = REQUIRED_EXCLUSIONS - set(cfg["excluded_paths"])
            if missing:
                errors.append(
                    f"rule: {name}: enabled assistants must exclude {sorted(missing)}"
                )

        features = cfg["features"]
        if features["agent_mode"] and features["public_code_matching"] != "block":
            errors.append(
                f"rule: {name}: agent_mode requires public_code_matching to be 'block'"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("policy", nargs="?", default=ROOT / "policy" / "policy.yaml")
    parser.add_argument("--schema", default=ROOT / "schema" / "policy.schema.json")
    args = parser.parse_args()

    try:
        policy = yaml.safe_load(Path(args.policy).read_text())
        schema = json.loads(Path(args.schema).read_text())
    except (OSError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read input: {exc}", file=sys.stderr)
        return 2

    errors = validate_schema(policy, schema)
    if not errors:  # rules assume a well-formed structure
        errors = validate_rules(policy)

    if errors:
        print(f"INVALID: {args.policy}")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"OK: {args.policy}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
