from __future__ import annotations

import argparse
import json
from pathlib import Path

from fraudgraph_sentinel.aura_config import (
    load_neo4j_config,
    merged_env,
    optional_env_status,
    required_env_status,
)
from fraudgraph_sentinel.aura_import import (
    get_driver,
    import_bundle,
    import_risk_bundle,
    inspect_labels,
    run_core_query_checks,
    smoke_test,
    verify_graph_counts,
)
from fraudgraph_sentinel.aura_queries import CORE_QUERY_TEMPLATES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Secret-safe AuraDB commands for FraudGraph Sentinel.")
    parser.add_argument("--env-file", default=".env", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("env-check")
    subparsers.add_parser("connect")
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("--bundle", default=Path("outputs/fraudgraph_sentinel"), type=Path)
    import_parser.add_argument("--batch-size", default=1_000, type=int)
    risk_parser = subparsers.add_parser("import-risk")
    risk_parser.add_argument("--bundle", default=Path("outputs/fraudgraph_sentinel_risk"), type=Path)
    risk_parser.add_argument("--batch-size", default=1_000, type=int)
    subparsers.add_parser("inspect")
    subparsers.add_parser("query-check")
    subparsers.add_parser("verify")
    subparsers.add_parser("queries")
    return parser


def print_env_status(env_file: Path) -> int:
    env = merged_env(env_file)
    for key, status in required_env_status(env).items():
        print(f"{key}: {status}")
    for key, status in optional_env_status(env).items():
        print(f"{key}: {status}")
    return 0 if all(status == "PRESENT" for status in required_env_status(env).values()) else 2


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "env-check":
        return print_env_status(args.env_file)
    if args.command == "queries":
        print(json.dumps([template.__dict__ for template in CORE_QUERY_TEMPLATES], indent=2))
        return 0

    config = load_neo4j_config(args.env_file)
    driver = get_driver(config)
    try:
        if args.command == "connect":
            print(f"AuraDB connectivity: {smoke_test(driver, config)}")
            return 0
        if args.command == "inspect":
            print(json.dumps(inspect_labels(driver, config), indent=2, default=str))
            return 0
        if args.command == "import":
            import_bundle(driver, config, args.bundle, batch_size=args.batch_size)
            print(json.dumps(verify_graph_counts(driver, config), indent=2, default=str))
            return 0
        if args.command == "import-risk":
            import_risk_bundle(driver, config, args.bundle, batch_size=args.batch_size)
            print(json.dumps(verify_graph_counts(driver, config), indent=2, default=str))
            return 0
        if args.command == "verify":
            print(json.dumps(verify_graph_counts(driver, config), indent=2, default=str))
            return 0
        if args.command == "query-check":
            print(json.dumps(run_core_query_checks(driver, config), indent=2, default=str))
            return 0
    finally:
        driver.close()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
