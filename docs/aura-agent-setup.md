# Aura Agent Setup

Use these steps after the compact graph has been imported into the existing AuraDB Free instance.

## Agent

Name: `FraudGraph Sentinel`

Description:

```text
A cyber-fraud investigation assistant that reasons over synthetic transaction paths, account relationships, repeated fraudulent destinations, and fraud-type patterns in Neo4j.
```

System instructions:

```text
You are FraudGraph Sentinel. Use Neo4j graph results to investigate synthetic cyber-fraud transaction patterns.

Ground every answer in graph findings. Prefer the provided Cypher Template tools for known fraud investigations. Use Text2Cypher only for ad-hoc read-only questions.

The dataset is synthetic. Do not claim that any account represents a real person, company, victim, criminal, or real-world crime.

Never perform writes or destructive operations. Do not generate CREATE, MERGE, DELETE, DETACH DELETE, SET, REMOVE, DROP, LOAD CSV, CALL dbms, or administration commands.

Explain suspicious patterns in plain language using relationships, counts, transaction type, amount, and account-neighborhood context.
```

## Graph Schema Context

```text
Nodes:
- Account(accountId)
- Transaction(transactionId, step, amount, isFraud, isFlaggedFraud, riskText)
- TransactionType(name)
- FraudLabel(name)

Relationships:
- (:Account)-[:SENT]->(:Transaction)
- (:Transaction)-[:TO]->(:Account)
- (:Transaction)-[:HAS_TYPE]->(:TransactionType)
- (:Transaction)-[:HAS_LABEL]->(:FraudLabel)
- (:Transaction)-[:HAS_RISK_INDICATOR]->(:RiskIndicator)
- (:EmailSample)-[:HAS_RISK_INDICATOR]->(:RiskIndicator)
- (:URLSample)-[:HAS_RISK_INDICATOR]->(:RiskIndicator)
```

## Required Tools

Use the generated machine-readable file:

```text
outputs/fraudgraph_sentinel/agent_tools.json
```

Configure these Cypher Template tools:

- `fraud_overview`
- `repeated_fraud_destinations`
- `high_value_fraud_paths`
- `account_fraud_neighborhood`
- `fraud_type_comparison`
- `fraud_concentration`
- `risk_indicator_overview`
- `shared_risk_indicator_context`

Enable Text2Cypher with the read-only system instructions above.

Skip Similarity Search for the zero-cost path unless embeddings are already configured and approved.

The optional risk-indicator tools are safe to use after `outputs/fraudgraph_sentinel_risk` has been imported. They connect separate synthetic datasets by shared risk indicators only; do not present them as causal attack chains.

## Manual Aura Console Steps

1. Open Aura Console.
2. Confirm the AuraDB Free instance is running.
3. Enable organization Generative AI assistance if it is not already enabled.
4. Open the database containing the imported FraudGraph Sentinel graph.
5. Create an Aura Agent named `FraudGraph Sentinel`.
6. Paste the agent description and system instructions from this document.
7. Add the six Cypher Template tools from `agent_tools.json`.
8. Add Text2Cypher using the graph schema context and read-only restrictions.
9. Test the demo questions in `docs/demo-script.md`.
10. Capture one graph screenshot and one agent-response screenshot for the hackathon reply.
