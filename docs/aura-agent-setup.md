# Aura Agent Setup

Use these steps after the compact graph has been imported into the existing AuraDB Free instance.

Official Aura Agent docs checked on 2026-05-29:

- Aura Agent supports Cypher Template, Similarity Search, and Text2Cypher tools.
- Internal agents are free to use; external agents incur charges.
- Import Agent can create an agent from JSON.
- Internal agents cannot also be enabled as MCP servers.

Reference: https://neo4j.com/docs/aura/aura-agent/

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

For the fastest setup, use Aura Console's **Import agent** flow and paste or upload:

```text
outputs/fraudgraph_sentinel/aura_agent_import_config.json
```

This import config is generated from the same source as `agent_tools.json`, keeps the agent `Internal`/private, and leaves MCP disabled for the zero-cost path.

If configuring manually, create these Cypher Template tools:

- `fraud_overview`
- `repeated_fraud_destinations`
- `high_value_fraud_paths`
- `account_fraud_neighborhood`
- `destination_fraud_profile`
- `fraud_type_comparison`
- `fraud_concentration`
- `risk_indicator_overview`
- `shared_risk_indicator_context`

Enable Text2Cypher with the read-only system instructions above.

Skip Similarity Search for the zero-cost path unless embeddings are already configured and approved.

If the import flow is unavailable, use `docs/create-with-ai-prompt.md` in the **Create with AI** dialog, then manually compare the generated tools against `agent_tools.json`.

The optional risk-indicator tools are safe to use after `outputs/fraudgraph_sentinel_risk` has been imported. They connect separate synthetic datasets by shared risk indicators only; do not present them as causal attack chains.

## Manual Aura Console Steps

1. Open Aura Console.
2. Confirm the AuraDB Free instance is running.
3. Enable organization Generative AI assistance if it is not already enabled.
4. Open the database containing the imported FraudGraph Sentinel graph.
5. Prefer **Import agent** and use `outputs/fraudgraph_sentinel/aura_agent_import_config.json`.
6. If importing is unavailable, create an Aura Agent named `FraudGraph Sentinel`.
7. Paste the agent description and system instructions from this document.
8. Add the nine Cypher Template tools from `agent_tools.json`.
9. Add Text2Cypher using the graph schema context and read-only restrictions.
10. Test the demo questions in `docs/demo-script.md`.
11. Capture one graph screenshot and one agent-response screenshot for the hackathon reply.
