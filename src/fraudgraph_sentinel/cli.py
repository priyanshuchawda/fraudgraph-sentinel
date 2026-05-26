from __future__ import annotations

import argparse
import json
from pathlib import Path

from fraudgraph_sentinel.agent_tools import (
    build_agent_tool_specs,
    build_aura_agent_import_config,
)
from fraudgraph_sentinel.cypher_export import export_graph_files
from fraudgraph_sentinel.sampling import sample_transactions_from_csv_with_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare FraudGraph Sentinel files for Neo4j Aura."
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to Synthetic_Financial_datasets_log.csv",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output directory for Neo4j import files",
    )
    parser.add_argument("--max-non-fraud", type=int, default=5_000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sample = sample_transactions_from_csv_with_stats(
        args.input, max_non_fraud=args.max_non_fraud
    )
    manifest = export_graph_files(
        sample.transactions, args.output, sample_stats=sample.stats
    )
    (args.output / "agent_tools.json").write_text(
        json.dumps(build_agent_tool_specs(), indent=2),
        encoding="utf-8",
    )
    (args.output / "aura_agent_import_config.json").write_text(
        json.dumps(build_aura_agent_import_config(), indent=2),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))
    return 0 if manifest["fitsConservativeAuraFree"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
