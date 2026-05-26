from __future__ import annotations

import csv
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path

from fraudgraph_sentinel.aura_config import Neo4jConfig
from fraudgraph_sentinel.graph_stats import (
    CONSERVATIVE_AURA_FREE_NODE_LIMIT,
    CONSERVATIVE_AURA_FREE_RELATIONSHIP_LIMIT,
)
from fraudgraph_sentinel.aura_queries import CORE_QUERY_TEMPLATES

CONSTRAINTS = (
    "CREATE CONSTRAINT account_id IF NOT EXISTS FOR (a:Account) REQUIRE a.accountId IS UNIQUE",
    "CREATE CONSTRAINT transaction_id IF NOT EXISTS FOR (t:Transaction) REQUIRE t.transactionId IS UNIQUE",
    "CREATE CONSTRAINT transaction_type_name IF NOT EXISTS FOR (t:TransactionType) REQUIRE t.name IS UNIQUE",
    "CREATE CONSTRAINT fraud_label_name IF NOT EXISTS FOR (l:FraudLabel) REQUIRE l.name IS UNIQUE",
)

ACCOUNT_IMPORT_CYPHER = """
UNWIND $rows AS row
MERGE (:Account {accountId: row.accountId})
"""

TRANSACTION_TYPE_IMPORT_CYPHER = """
UNWIND $rows AS row
MERGE (:TransactionType {name: row.name})
"""

FRAUD_LABEL_IMPORT_CYPHER = """
UNWIND $rows AS row
MERGE (:FraudLabel {name: row.name})
"""

TRANSACTION_IMPORT_CYPHER = """
UNWIND $rows AS row
MERGE (tx:Transaction {transactionId: row.transactionId})
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
MATCH (origin:Account {accountId: row.origin})
MATCH (destination:Account {accountId: row.destination})
MATCH (kind:TransactionType {name: row.type})
MATCH (label:FraudLabel {name: row.fraudLabel})
MERGE (origin)-[:SENT]->(tx)
MERGE (tx)-[:TO]->(destination)
MERGE (tx)-[:HAS_TYPE]->(kind)
MERGE (tx)-[:HAS_LABEL]->(label)
"""


def get_driver(config: Neo4jConfig):
    try:
        from neo4j import GraphDatabase
    except ImportError as error:
        raise RuntimeError("The official neo4j Python driver is required. Install project dependencies first.") from error
    return GraphDatabase.driver(config.uri, auth=(config.username, config.password))


def chunk_rows(rows: Iterable[dict[str, str]], *, size: int) -> Iterator[list[dict[str, str]]]:
    batch: list[dict[str, str]] = []
    for row in rows:
        batch.append(row)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def run_write_batch(tx, cypher: str, rows: Sequence[dict[str, str]]) -> None:
    tx.run(cypher, rows=list(rows)).consume()


def create_constraints(session) -> None:
    for cypher in CONSTRAINTS:
        session.run(cypher).consume()


def import_bundle(driver, config: Neo4jConfig, bundle_dir: Path | str, *, batch_size: int = 1_000) -> None:
    bundle = Path(bundle_dir)
    with driver.session(database=config.database) as session:
        create_constraints(session)
        for filename, cypher in (
            ("accounts.csv", ACCOUNT_IMPORT_CYPHER),
            ("transaction_types.csv", TRANSACTION_TYPE_IMPORT_CYPHER),
            ("fraud_labels.csv", FRAUD_LABEL_IMPORT_CYPHER),
            ("transactions.csv", TRANSACTION_IMPORT_CYPHER),
        ):
            for batch in chunk_rows(read_csv_rows(bundle / filename), size=batch_size):
                session.execute_write(run_write_batch, cypher, batch)


def build_count_verification_query() -> str:
    return """
MATCH (n)
WHERE n:Account OR n:Transaction OR n:TransactionType OR n:FraudLabel
WITH count(n) AS nodes
MATCH ()-[r]->()
WHERE type(r) IN ['SENT', 'TO', 'HAS_TYPE', 'HAS_LABEL']
WITH nodes, count(r) AS relationships
MATCH (tx:Transaction)
WITH nodes, relationships, count(tx) AS transactions, sum(CASE WHEN tx.isFraud THEN 1 ELSE 0 END) AS fraudTransactions
MATCH (kind:TransactionType)
RETURN nodes,
       relationships,
       transactions,
       fraudTransactions,
       collect(kind.name) AS transactionTypes,
       nodes <= $nodeLimit AS nodeLimitSafe,
       relationships <= $relationshipLimit AS relationshipLimitSafe
"""


def verify_graph_counts(driver, config: Neo4jConfig) -> dict[str, object]:
    with driver.session(database=config.database) as session:
        record = session.run(
            build_count_verification_query(),
            nodeLimit=CONSERVATIVE_AURA_FREE_NODE_LIMIT,
            relationshipLimit=CONSERVATIVE_AURA_FREE_RELATIONSHIP_LIMIT,
        ).single()
    return dict(record) if record else {}


def inspect_labels(driver, config: Neo4jConfig) -> list[dict[str, object]]:
    with driver.session(database=config.database) as session:
        records = session.run(
            """
MATCH (n)
UNWIND labels(n) AS label
RETURN label, count(*) AS nodes
ORDER BY label
"""
        )
        return [dict(record) for record in records]


def run_core_query_checks(driver, config: Neo4jConfig) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    with driver.session(database=config.database) as session:
        for template in CORE_QUERY_TEMPLATES:
            records = list(session.run(template.cypher, **template.parameters))
            first = dict(records[0]) if records else {}
            checks.append(
                {
                    "name": template.name,
                    "rows": len(records),
                    "columns": list(first.keys()),
                    "hasResults": bool(records),
                }
            )
    return checks


def smoke_test(driver, config: Neo4jConfig) -> str:
    with driver.session(database=config.database) as session:
        value = session.run("RETURN 1 AS ok").single()
    return "PASS" if value and value["ok"] == 1 else "FAIL"
