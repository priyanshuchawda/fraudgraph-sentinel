from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from collections.abc import Iterable
from pathlib import Path

from fraudgraph_sentinel.graph_stats import estimate_graph_size
from fraudgraph_sentinel.model import Transaction
from fraudgraph_sentinel.sampling import SampleStats


def _write_dicts(
    path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]
) -> int:
    count = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def export_graph_files(
    transactions: Iterable[Transaction],
    output_dir: Path | str,
    *,
    sample_stats: SampleStats | None = None,
) -> dict[str, int | str | bool]:
    rows = list(transactions)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    accounts = sorted({tx.origin for tx in rows} | {tx.destination for tx in rows})
    types = sorted({tx.transaction_type for tx in rows})
    labels = sorted({tx.fraud_label for tx in rows})

    _write_dicts(
        target / "accounts.csv",
        ["accountId"],
        ({"accountId": account} for account in accounts),
    )
    _write_dicts(
        target / "transaction_types.csv", ["name"], ({"name": name} for name in types)
    )
    _write_dicts(
        target / "fraud_labels.csv", ["name"], ({"name": name} for name in labels)
    )
    _write_dicts(
        target / "transactions.csv",
        [
            "transactionId",
            "step",
            "type",
            "amount",
            "origin",
            "oldBalanceOrigin",
            "newBalanceOrigin",
            "destination",
            "oldBalanceDestination",
            "newBalanceDestination",
            "isFraud",
            "isFlaggedFraud",
            "fraudLabel",
            "riskText",
        ],
        (
            {
                "transactionId": tx.transaction_id,
                "step": tx.step,
                "type": tx.transaction_type,
                "amount": f"{tx.amount:.2f}",
                "origin": tx.origin,
                "oldBalanceOrigin": f"{tx.old_balance_origin:.2f}",
                "newBalanceOrigin": f"{tx.new_balance_origin:.2f}",
                "destination": tx.destination,
                "oldBalanceDestination": f"{tx.old_balance_destination:.2f}",
                "newBalanceDestination": f"{tx.new_balance_destination:.2f}",
                "isFraud": str(tx.is_fraud).lower(),
                "isFlaggedFraud": str(tx.is_flagged_fraud).lower(),
                "fraudLabel": tx.fraud_label,
                "riskText": tx.risk_text,
            }
            for tx in rows
        ),
    )

    estimate = estimate_graph_size(rows)
    manifest: dict[str, int | str | bool] = {
        "sourceDataset": sample_stats.source_dataset if sample_stats else "unknown",
        "sourceRows": sample_stats.source_rows if sample_stats else 0,
        "fraudRowsSelected": sample_stats.fraud_rows_selected
        if sample_stats
        else sum(tx.is_fraud for tx in rows),
        "nonFraudRowsSampled": sample_stats.non_fraud_rows_sampled
        if sample_stats
        else sum(not tx.is_fraud for tx in rows),
        "samplingRule": sample_stats.sampling_rule
        if sample_stats
        else "all_fraud_plus_first_n_non_fraud",
        "deterministicSeed": sample_stats.deterministic_seed
        if sample_stats
        else "not_applicable_first_n",
        "generationDateUtc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "accounts": estimate.accounts,
        "transactions": estimate.transactions,
        "transactionTypes": estimate.transaction_types,
        "fraudLabels": estimate.fraud_labels,
        "nodes": estimate.nodes,
        "relationships": estimate.relationships,
        "fitsConservativeAuraFree": estimate.fits_conservative_aura_free,
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    (target / "import.cypher").write_text(
        render_import_cypher("$IMPORT_BASE_URL"), encoding="utf-8"
    )
    return manifest


def render_import_cypher(base_url: str) -> str:
    root = base_url.rstrip("/")
    return f"""CREATE CONSTRAINT account_id IF NOT EXISTS FOR (a:Account) REQUIRE a.accountId IS UNIQUE;
CREATE CONSTRAINT transaction_id IF NOT EXISTS FOR (t:Transaction) REQUIRE t.transactionId IS UNIQUE;
CREATE CONSTRAINT transaction_type_name IF NOT EXISTS FOR (t:TransactionType) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT fraud_label_name IF NOT EXISTS FOR (l:FraudLabel) REQUIRE l.name IS UNIQUE;
CREATE VECTOR INDEX transaction_risk_text IF NOT EXISTS
FOR (t:Transaction) ON (t.embedding)
OPTIONS {{indexConfig: {{`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}}};

LOAD CSV WITH HEADERS FROM '{root}/accounts.csv' AS row
MERGE (:Account {{accountId: row.accountId}});

LOAD CSV WITH HEADERS FROM '{root}/transaction_types.csv' AS row
MERGE (:TransactionType {{name: row.name}});

LOAD CSV WITH HEADERS FROM '{root}/fraud_labels.csv' AS row
MERGE (:FraudLabel {{name: row.name}});

LOAD CSV WITH HEADERS FROM '{root}/transactions.csv' AS row
MERGE (tx:Transaction {{transactionId: row.transactionId}})
SET tx.step = toInteger(row.step),
    tx.amount = toFloat(row.amount),
    tx.oldBalanceOrigin = toFloat(row.oldBalanceOrigin),
    tx.newBalanceOrigin = toFloat(row.newBalanceOrigin),
    tx.oldBalanceDestination = toFloat(row.oldBalanceDestination),
    tx.newBalanceDestination = toFloat(row.newBalanceDestination),
    tx.isFraud = row.isFraud = 'true',
    tx.isFlaggedFraud = row.isFlaggedFraud = 'true',
    tx.riskText = row.riskText
WITH tx, row
MATCH (origin:Account {{accountId: row.origin}})
MATCH (destination:Account {{accountId: row.destination}})
MATCH (kind:TransactionType {{name: row.type}})
MATCH (label:FraudLabel {{name: row.fraudLabel}})
MERGE (origin)-[:SENT]->(tx)
MERGE (tx)-[:TO]->(destination)
MERGE (tx)-[:HAS_TYPE]->(kind)
MERGE (tx)-[:HAS_LABEL]->(label);
"""
