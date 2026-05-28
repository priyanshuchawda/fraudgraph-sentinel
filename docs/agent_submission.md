# FraudGraph Sentinel

## Agent Name

FraudGraph Sentinel

## What It Does

FraudGraph Sentinel is a graph-backed cyber-fraud investigation assistant for a synthetic mobile-money dataset. It helps analysts reason over suspicious transaction paths, repeated fraudulent destinations, high-value fraud movements, fraud-type patterns, and account neighborhoods.

It grounds answers in Neo4j graph results and explains why a pattern is suspicious without claiming real-world criminal activity.

## Dataset And Why A Graph Fits

Dataset: `Synthetic_Financial_datasets_log.csv`

The source dataset contains **6,362,620** synthetic transaction rows with origin accounts, destination accounts, transaction type, amount, account balances, and fraud labels.

A graph fits because fraud is relational. Repeated recipients, shared counterparties, source-to-transaction-to-destination paths, and fraud concentration are easier to inspect as connected entities than as isolated table rows.

The AuraDB Free build uses:

- all **8,213** fraud rows
- **5,000** deterministic non-fraud sample rows
- **37,585** total nodes
- **52,852** total relationships

This stays below the conservative project safety target of **50,000 nodes** and **175,000 relationships**.

## Tools Used

- Cypher Template
- Text2Cypher

Prepared Cypher Template tools:

- `fraud_overview`
- `repeated_fraud_destinations`
- `high_value_fraud_paths`
- `account_fraud_neighborhood`
- `fraud_type_comparison`
- `fraud_concentration`
- `risk_indicator_overview`
- `shared_risk_indicator_context`

Optional future tool:

- Similarity Search over `Transaction.riskText` if embeddings are enabled.

## Verified AuraDB Import

Base AuraDB verification:

- Nodes: **37,585**
- Relationships: **52,852**
- Transactions: **13,213**
- Fraud transactions: **8,213**
- Free-tier safety: **pass**

Optional ScamChain-style risk-indicator enhancement:

- Email samples: **800**
- URL samples: **400**
- Risk indicators: **12**
- Enhanced nodes: **38,797**
- Enhanced relationships: **74,262**
- Causality claim: **false**. The datasets are linked only through shared risk indicators, not real attack-chain causality.

Validated queries:

- fraud overview
- repeated fraudulent destinations
- high-value fraud paths
- account fraud neighborhood
- fraud type comparison
- fraud concentration
- risk indicator overview
- shared risk indicator context

Aura Console setup files:

- `outputs/fraudgraph_sentinel/agent_tools.json`
- `outputs/fraudgraph_sentinel/aura_agent_import_config.json`

## GitHub Repository

https://github.com/priyanshuchawda/fraudgraph-sentinel

## Screenshots To Add

1. Aura Console graph screenshot showing `Account`, `Transaction`, `TransactionType`, and `FraudLabel` nodes.
2. Aura Agent response screenshot for:

```text
Which destination accounts received multiple fraudulent transfers?
```

Use `docs/hackathon-thread-reply.md` as the final copy-paste submission reply after screenshots are captured.

## Optional Agent Link

Not published. Aura Console demo is sufficient for the free-path submission unless public publishing is separately approved after checking pricing or credits.
