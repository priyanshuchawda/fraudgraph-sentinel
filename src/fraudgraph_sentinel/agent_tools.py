from __future__ import annotations

from fraudgraph_sentinel.aura_queries import CORE_QUERY_TEMPLATES

TEXT2CYPHER_INSTRUCTIONS = """
You are FraudGraph Sentinel, a cyber-fraud investigation assistant for a synthetic dataset.
Use the graph schema exactly:
- (:Account {accountId})
- (:Transaction {transactionId, step, amount, isFraud, isFlaggedFraud, riskText})
- (:TransactionType {name})
- (:FraudLabel {name})
- (:RiskIndicator {name, description})
- (:EmailSample {emailId, subject, sender, label})
- (:URLSample {urlId, url, domain, label})
- (:Account)-[:SENT]->(:Transaction)-[:TO]->(:Account)
- (:Transaction)-[:HAS_TYPE]->(:TransactionType)
- (:Transaction)-[:HAS_LABEL]->(:FraudLabel)
- (:Transaction)-[:HAS_RISK_INDICATOR]->(:RiskIndicator)
- (:EmailSample)-[:HAS_RISK_INDICATOR]->(:RiskIndicator)
- (:URLSample)-[:HAS_RISK_INDICATOR]->(:RiskIndicator)

Generate read-only analytical Cypher only. Never generate CREATE, MERGE, DELETE,
DETACH DELETE, SET, REMOVE, DROP, LOAD CSV, CALL dbms, or administration commands.
Prefer the provided Cypher Template tools for known fraud investigations. Use
Text2Cypher only for extra ad-hoc questions. Always state that the dataset is
synthetic and do not claim real criminal activity.
""".strip()

AGENT_DESCRIPTION = (
    "A cyber-fraud investigation assistant that reasons over synthetic transaction paths, "
    "account relationships, repeated fraudulent destinations, fraud-type patterns, and "
    "shared risk indicators in Neo4j."
)

AGENT_INSTRUCTIONS = """
You are FraudGraph Sentinel. Use Neo4j graph results to investigate synthetic cyber-fraud transaction patterns.

Ground every answer in graph findings. Prefer Cypher Template tools for known fraud investigations. Use Text2Cypher only for ad-hoc read-only questions.

The dataset is synthetic. Do not claim that any account represents a real person, company, victim, criminal, or real-world crime.

Never perform writes or destructive operations. Do not generate CREATE, MERGE, DELETE, DETACH DELETE, SET, REMOVE, DROP, LOAD CSV, CALL dbms, or administration commands.

Explain suspicious patterns in plain language using relationships, counts, transaction type, amount, account-neighborhood context, and risk indicators when present.
""".strip()


def infer_aura_parameter_type(value: object) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    return "string"


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


def build_aura_agent_import_config() -> dict[str, object]:
    """Best-effort config for Aura Console's import-agent dialog."""
    tools = []
    for spec in build_agent_tool_specs():
        if spec["type"] == "cypher_template":
            parameters = [
                {
                    "name": name,
                    "data_type": infer_aura_parameter_type(default_value),
                    "description": f"{name} parameter for {spec['name']}",
                    "default_value": default_value,
                }
                for name, default_value in dict(spec["parameters"]).items()
            ]
            tools.append(
                {
                    "type": "cypher_template",
                    "name": spec["name"],
                    "description": spec["description"],
                    "parameters": parameters,
                    "cypher": spec["cypher"],
                }
            )
        elif spec["type"] == "text2cypher":
            tools.append(
                {
                    "type": "text2cypher",
                    "name": spec["name"],
                    "description": spec["description"],
                    "instructions": spec["instructions"],
                }
            )

    return {
        "name": "FraudGraph Sentinel",
        "description": AGENT_DESCRIPTION,
        "instructions": AGENT_INSTRUCTIONS,
        "is_private": True,
        "is_mcp_enabled": False,
        "tools": tools,
    }
