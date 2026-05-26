from __future__ import annotations

import csv
from dataclasses import dataclass
from collections.abc import Iterable, Iterator
from pathlib import Path

from fraudgraph_sentinel.model import Transaction

REQUIRED_COLUMNS = (
    "step",
    "type",
    "amount",
    "nameOrig",
    "oldbalanceOrg",
    "newbalanceOrig",
    "nameDest",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
    "isFlaggedFraud",
)


@dataclass(frozen=True)
class SampleStats:
    source_dataset: str
    source_rows: int
    fraud_rows_selected: int
    non_fraud_rows_sampled: int
    sampling_rule: str = "all_fraud_plus_first_n_non_fraud"
    deterministic_seed: str = "not_applicable_first_n"


@dataclass(frozen=True)
class SampleResult:
    transactions: list[Transaction]
    stats: SampleStats


def _validate_columns(fieldnames: list[str] | None) -> None:
    actual = set(fieldnames or [])
    missing = [column for column in REQUIRED_COLUMNS if column not in actual]
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")


def iter_transactions(path: Path | str) -> Iterator[Transaction]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        _validate_columns(reader.fieldnames)
        for row in reader:
            yield Transaction.from_csv_row(row)


def sample_transactions(
    transactions: Iterable[Transaction],
    *,
    max_non_fraud: int,
) -> list[Transaction]:
    sampled: list[Transaction] = []
    non_fraud_count = 0
    for tx in transactions:
        if tx.is_fraud:
            sampled.append(tx)
        elif non_fraud_count < max_non_fraud:
            sampled.append(tx)
            non_fraud_count += 1
    return sampled


def sample_transactions_from_csv(
    path: Path | str, *, max_non_fraud: int
) -> list[Transaction]:
    return sample_transactions_from_csv_with_stats(
        path, max_non_fraud=max_non_fraud
    ).transactions


def sample_transactions_from_csv_with_stats(
    path: Path | str, *, max_non_fraud: int
) -> SampleResult:
    sampled: list[Transaction] = []
    non_fraud_count = 0
    fraud_count = 0
    source_rows = 0
    source_path = Path(path)
    with source_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        _validate_columns(reader.fieldnames)
        for row in reader:
            source_rows += 1
            is_fraud = row["isFraud"] == "1"
            if is_fraud or non_fraud_count < max_non_fraud:
                sampled.append(Transaction.from_csv_row(row))
                if is_fraud:
                    fraud_count += 1
                else:
                    non_fraud_count += 1
    return SampleResult(
        transactions=sampled,
        stats=SampleStats(
            source_dataset=source_path.name,
            source_rows=source_rows,
            fraud_rows_selected=fraud_count,
            non_fraud_rows_sampled=non_fraud_count,
        ),
    )
