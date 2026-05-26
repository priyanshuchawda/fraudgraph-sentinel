from fraudgraph_sentinel.aura_import import (
    ACCOUNT_IMPORT_CYPHER,
    TRANSACTION_IMPORT_CYPHER,
    build_count_verification_query,
    chunk_rows,
)


def test_import_queries_are_parameterized_unwind_queries():
    assert "UNWIND $rows AS row" in ACCOUNT_IMPORT_CYPHER
    assert "UNWIND $rows AS row" in TRANSACTION_IMPORT_CYPHER
    assert "LOAD CSV" not in TRANSACTION_IMPORT_CYPHER
    assert "MERGE (origin)-[:SENT]->(tx)" in TRANSACTION_IMPORT_CYPHER


def test_chunk_rows_batches_iterables():
    chunks = list(chunk_rows(({"n": i} for i in range(5)), size=2))

    assert chunks == [[{"n": 0}, {"n": 1}], [{"n": 2}, {"n": 3}], [{"n": 4}]]


def test_count_verification_query_is_read_only():
    query = build_count_verification_query()

    assert "MATCH" in query
    assert "CREATE" not in query
    assert "DELETE" not in query
