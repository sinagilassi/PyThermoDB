#!/usr/bin/env python
"""Smoke-test pyThermoDB reference builders from the command line."""

from __future__ import annotations

import argparse
import json
import os
import pprint
import sys
from pathlib import Path
from typing import Any


def _ensure_local_project_imports() -> None:
    candidates = [
        Path.cwd(),
        Path(__file__).resolve().parents[3],
    ]

    for candidate in candidates:
        if (candidate / "pyThermoDB").is_dir():
            candidate_text = str(candidate)
            if candidate_text not in sys.path:
                sys.path.insert(0, candidate_text)
            return


def _split_csv(values: list[str] | None) -> list[str] | None:
    if not values:
        return None

    result: list[str] = []
    for value in values:
        for item in value.split(","):
            item = item.strip()
            if item:
                result.append(item)

    return result or None


def _reference_arg(value: str) -> str:
    if os.path.exists(value):
        return os.path.abspath(value)
    return value


def _load_components(value: str) -> list[Any]:
    from pythermodb_settings.models import Component

    raw = value
    if os.path.exists(value):
        with open(value, "r", encoding="utf-8") as handle:
            raw = handle.read()

    try:
        records = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid components JSON: {exc}") from exc

    if not isinstance(records, list):
        raise SystemExit("Components JSON must be a list of objects.")

    components = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise SystemExit(f"Component #{index} must be an object.")

        missing = {"name", "formula", "state"} - set(record)
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise SystemExit(f"Component #{index} missing: {missing_list}")

        components.append(
            Component(
                name=record["name"],
                formula=record["formula"],
                state=record["state"],
            )
        )

    return components


def _save_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    if not args.save_dir:
        return {}

    kwargs: dict[str, Any] = {
        "thermodb_save": True,
        "thermodb_save_path": os.path.abspath(args.save_dir),
    }
    if args.thermodb_name:
        kwargs["thermodb_name"] = args.thermodb_name
    return kwargs


def _unwrap_thermodb(result: Any) -> Any:
    return getattr(result, "thermodb", result)


def _print_result(result: Any) -> None:
    if result is None:
        raise SystemExit("Build returned None.")

    thermodb = _unwrap_thermodb(result)
    print(f"result_type: {type(result).__name__}")
    print(f"thermodb_type: {type(thermodb).__name__}")

    check = getattr(thermodb, "check", None)
    if callable(check):
        print("check:")
        pprint.pp(check())
    else:
        print("check: unavailable")


def _validate_component(args: argparse.Namespace) -> None:
    from pyThermoDB import build_component_thermodb_from_reference

    result = build_component_thermodb_from_reference(
        component_name=args.name,
        component_formula=args.formula,
        component_state=args.state,
        reference_content=_reference_arg(args.reference),
        ignore_state_props=_split_csv(args.ignore_state_props),
        mode=args.mode,
        **_save_kwargs(args),
    )
    _print_result(result)


def _validate_mixture(args: argparse.Namespace) -> None:
    from pyThermoDB import build_mixture_thermodb_from_reference

    result = build_mixture_thermodb_from_reference(
        components=_load_components(args.components),
        reference_content=_reference_arg(args.reference),
        mixture_names=_split_csv(args.mixture_names),
        ignore_state_props=_split_csv(args.ignore_state_props),
        verbose=args.verbose,
        **_save_kwargs(args),
    )
    _print_result(result)


def _validate_constants(args: argparse.Namespace) -> None:
    from pyThermoDB import build_constants_thermodb_from_reference

    result = build_constants_thermodb_from_reference(
        reference_content=_reference_arg(args.reference),
        databook_name=args.databook_name,
        table_name=args.table_name,
        constants=_split_csv(args.constants),
        verbose=args.verbose,
        **_save_kwargs(args),
    )
    _print_result(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate pyThermoDB reference builds for components, mixtures, or constants."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--reference",
        required=True,
        help="Reference YAML content or path to a YAML reference file.",
    )
    common.add_argument(
        "--ignore-state-props",
        nargs="*",
        help="Property symbols whose state checks should be ignored. Accepts spaces or commas.",
    )
    common.add_argument(
        "--save-dir",
        help="Optional directory for saving the generated ThermoDB.",
    )
    common.add_argument(
        "--thermodb-name",
        help="Optional saved ThermoDB name. Used only with --save-dir.",
    )
    common.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose builder output when supported.",
    )

    component = subparsers.add_parser(
        "component",
        parents=[common],
        help="Validate build_component_thermodb_from_reference.",
    )
    component.add_argument("--name", required=True, help="Component name.")
    component.add_argument("--formula", required=True, help="Component formula.")
    component.add_argument("--state", required=True, help="Component state.")
    component.add_argument(
        "--mode",
        default="log",
        help="Builder mode for component builds. Defaults to 'log'.",
    )
    component.set_defaults(func=_validate_component)

    mixture = subparsers.add_parser(
        "mixture",
        parents=[common],
        help="Validate build_mixture_thermodb_from_reference.",
    )
    mixture.add_argument(
        "--components",
        required=True,
        help='JSON string or JSON file path, e.g. [{"name":"methanol","formula":"CH3OH","state":"l"}].',
    )
    mixture.add_argument(
        "--mixture-names",
        nargs="*",
        help="Optional mixture names. Accepts spaces or commas.",
    )
    mixture.set_defaults(func=_validate_mixture)

    constants = subparsers.add_parser(
        "constants",
        parents=[common],
        help="Validate build_constants_thermodb_from_reference.",
    )
    constants.add_argument("--databook-name", help="Optional databook filter.")
    constants.add_argument("--table-name", help="Optional constants table filter.")
    constants.add_argument(
        "--constants",
        nargs="*",
        help="Optional constant symbols/names to select. Accepts spaces or commas.",
    )
    constants.set_defaults(func=_validate_constants)

    return parser


def main(argv: list[str] | None = None) -> int:
    _ensure_local_project_imports()

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        args.func(args)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
