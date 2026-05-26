from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

from fraudgraph_sentinel.model import Transaction


CONSERVATIVE_AURA_FREE_NODE_LIMIT = 50_000
CONSERVATIVE_AURA_FREE_RELATIONSHIP_LIMIT = 175_000


@dataclass(frozen=True)
class GraphSizeEstimate:
    accounts: int
    transactions: int
    transaction_types: int
    fraud_labels: int
    nodes: int
    relationships: int
    fits_conservative_aura_free: bool


def estimate_graph_size(transactions: Iterable[Transaction]) -> GraphSizeEstimate:
    rows = list(transactions)
    accounts = {tx.origin for tx in rows} | {tx.destination for tx in rows}
    transaction_types = {tx.transaction_type for tx in rows}
    fraud_labels = {tx.fraud_label for tx in rows}
    nodes = len(accounts) + len(rows) + len(transaction_types) + len(fraud_labels)
    relationships = len(rows) * 4
    return GraphSizeEstimate(
        accounts=len(accounts),
        transactions=len(rows),
        transaction_types=len(transaction_types),
        fraud_labels=len(fraud_labels),
        nodes=nodes,
        relationships=relationships,
        fits_conservative_aura_free=(
            nodes <= CONSERVATIVE_AURA_FREE_NODE_LIMIT
            and relationships <= CONSERVATIVE_AURA_FREE_RELATIONSHIP_LIMIT
        ),
    )
