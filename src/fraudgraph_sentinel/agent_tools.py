from __future__ import annotations


def build_agent_tool_specs() -> list[dict[str, object]]:
    return [
        {
            "name": "Find repeated fraud destinations",
            "type": "cypher_template",
            "description": "Find destination accounts receiving multiple fraudulent transactions.",
            "parameters": {"minFraudTransactions": 2, "limit": 10},
            "cypher": (
                "MATCH (origin:Account)-[:SENT]->(tx:Transaction {isFraud: true})-[:TO]->(dest:Account) "
                "WITH dest, count(tx) AS fraudCount, sum(tx.amount) AS fraudAmount, collect(origin.accountId)[0..5] AS sampleOrigins "
                "WHERE fraudCount >= $minFraudTransactions "
                "RETURN dest.accountId AS destination, fraudCount, fraudAmount, sampleOrigins "
                "ORDER BY fraudCount DESC, fraudAmount DESC LIMIT $limit"
            ),
        },
        {
            "name": "Explain account neighborhood",
            "type": "cypher_template",
            "description": "Show direct suspicious transaction context around one account.",
            "parameters": {"accountId": "C840083671", "limit": 25},
            "cypher": (
                "MATCH path=(account:Account {accountId: $accountId})-[:SENT|TO]-(tx:Transaction)-[:SENT|TO]-(other:Account) "
                "RETURN path LIMIT $limit"
            ),
        },
        {
            "name": "Natural language graph questions",
            "type": "text2cypher",
            "description": "Answer flexible questions about accounts, transactions, fraud labels, and transaction types.",
            "schema_hint": (
                "Nodes: Account(accountId), Transaction(transactionId, amount, step, isFraud, "
                "isFlaggedFraud, riskText), TransactionType(name), FraudLabel(name). "
                "Relationships: (:Account)-[:SENT]->(:Transaction)-[:TO]->(:Account), "
                "(:Transaction)-[:HAS_TYPE]->(:TransactionType), (:Transaction)-[:HAS_LABEL]->(:FraudLabel)."
            ),
        },
        {
            "name": "Similar fraud case search",
            "type": "similarity_search",
            "description": "Find transactions semantically similar to a described suspicious case using Transaction.riskText.",
            "optional": True,
            "cost_note": "Enable only if an embedding provider is configured; Cypher Templates and Text2Cypher are enough for the zero-cost submission path.",
            "index": "transaction_risk_text",
            "node_label": "Transaction",
            "text_property": "riskText",
            "embedding_property": "embedding",
        },
    ]
