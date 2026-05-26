from __future__ import annotations

import argparse
import json
from pathlib import Path

from fraudgraph_sentinel.risk_enhancement import export_risk_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build optional ScamChain risk-indicator sample bundle.")
    parser.add_argument("--email-xlsx", required=True, type=Path)
    parser.add_argument("--url-csv", required=True, type=Path)
    parser.add_argument("--transactions-csv", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-phishing-urls", default=300, type=int)
    parser.add_argument("--max-legitimate-urls", default=100, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = export_risk_bundle(
        email_xlsx=args.email_xlsx,
        url_csv=args.url_csv,
        transactions_csv=args.transactions_csv,
        output_dir=args.output,
        max_phishing_urls=args.max_phishing_urls,
        max_legitimate_urls=args.max_legitimate_urls,
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
