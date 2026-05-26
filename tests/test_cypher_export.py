import csv

from fraudgraph_sentinel.cypher_export import export_graph_files, render_import_cypher
from fraudgraph_sentinel.model import Transaction
from fraudgraph_sentinel.sampling import SampleStats


def test_export_graph_files_writes_nodes_and_relationships(tmp_path):
    transactions = [
        Transaction(
            step=1,
            transaction_type="TRANSFER",
            amount=181.0,
            origin="C1",
            old_balance_origin=181.0,
            new_balance_origin=0.0,
            destination="C2",
            old_balance_destination=0.0,
            new_balance_destination=181.0,
            is_fraud=True,
            is_flagged_fraud=False,
        )
    ]

    manifest = export_graph_files(
        transactions,
        tmp_path,
        sample_stats=SampleStats(
            source_dataset="fixture.csv",
            source_rows=1,
            fraud_rows_selected=1,
            non_fraud_rows_sampled=0,
        ),
    )

    assert manifest["transactions"] == 1
    assert manifest["accounts"] == 2
    assert manifest["sourceDataset"] == "fixture.csv"
    assert manifest["sourceRows"] == 1
    assert manifest["fraudRowsSelected"] == 1
    assert manifest["nonFraudRowsSampled"] == 0
    assert manifest["samplingRule"] == "all_fraud_plus_first_n_non_fraud"
    assert manifest["deterministicSeed"] == "not_applicable_first_n"
    assert "generationDateUtc" in manifest
    with (tmp_path / "transactions.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["transactionId"] == "tx-1-C1-C2"
    assert rows[0]["riskText"].startswith("Fraudulent TRANSFER")


def test_import_cypher_contains_constraints_and_load_csv_statements():
    cypher = render_import_cypher(base_url="https://example.com/import")

    assert "CREATE CONSTRAINT account_id" in cypher
    assert (
        "LOAD CSV WITH HEADERS FROM 'https://example.com/import/accounts.csv'" in cypher
    )
    assert "MERGE (origin)-[:SENT]->(tx)" in cypher
