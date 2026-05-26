from __future__ import annotations

from fraudgraph_sentinel.aura_queries import CORE_QUERY_TEMPLATES

TEXT2CYPHER_INSTRUCTIONS = """
You are FraudGraph Sentinel, a cyber-fraud investigation assistant for a synthetic dataset.
Use the graph schema exactly:
- (:Account {accountId})
- (:Transaction {transactionId, step, amount, isFraud, isFlaggedFraud, riskText})
- (:TransactionType {name})
- (:FraudLabel {name})
- (:Account)-[:SENT]->(:Transaction)-[:TO]->(:Account)
- (:Transaction)-[:HAS_TYPE]->(:TransactionType)
- (:Transaction)-[:HAS_LABEL]->(:FraudLabel)

Generate read-only analytical Cypher only. Never generate CREATE, MERGE, DELETE,
DETACH DELETE, SET, REMOVE, DROP, LOAD CSV, CALL dbms, or administration commands.
Prefer the provided Cypher Template tools for known fraud investigations. Use
Text2Cypher only for extra ad-hoc questions. Always state that the dataset is
synthetic and do not claim real criminal activity.
""".strip()


def build_agent_tool_specs() -> list[dict[str, object]]:
    template_specs = [
        {
            "name": template.name,
            "type": "cypher_template",
            "description": template.description,
            "parameters": template.parameters,
            "cypher": template.cypher.strip(),
            "example_questions": list(template.example_questions),
            "expected_output": template.expected_output,
        }
        for template in CORE_QUERY_TEMPLATES
    ]
    return template_specs + [
        {
            "name": "natural_language_graph_questions",
            "type": "text2cypher",
            "description": "Read-only flexible fallback for ad-hoc graph questions not covered by templates.",
            "instructions": TEXT2CYPHER_INSTRUCTIONS,
        },
        {
            "name": "Similar fraud case search",
            "type": "similarity_search",
            "description": "Optional similar-case search over Transaction.riskText.",
            "optional": True,
            "cost_note": "Enable only if an embedding provider is configured; skip for the zero-cost path.",
            "index": "transaction_risk_text",
            "node_label": "Transaction",
            "text_property": "riskText",
            "embedding_property": "embedding",
        },
    ]
