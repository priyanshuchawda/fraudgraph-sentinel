# FraudGraph Sentinel

## Agent Name

FraudGraph Sentinel

## What It Does

FraudGraph Sentinel is a graph-backed AI investigation agent for synthetic mobile-money fraud. It answers questions about suspicious account movement, repeated fraud destinations, high-value fraud transfers, fraud labels, and transaction-type patterns.

Example questions:

- Which destination accounts receive repeated fraud transfers?
- Which transaction type has the highest fraud rate?
- Explain the suspicious neighborhood around account `C840083671`.
- Find similar fraud cases where the sender balance was drained.

## Dataset And Why A Graph Fits

Dataset: `Synthetic_Financial_datasets_log.csv`

The source file contains 6,362,620 transaction rows with origin accounts, destination accounts, transaction types, amounts, balances, and fraud labels. A graph fits because fraud is relational: suspicious behavior is often visible through repeated destinations, shared accounts, transaction paths, and multi-hop account neighborhoods rather than isolated rows.

The Aura Free build uses all 8,213 fraud rows and a bounded non-fraud sample so the graph stays small while preserving the most important investigation signal.

## Graph Model

```text
(:Account)-[:SENT]->(:Transaction)-[:TO]->(:Account)
(:Transaction)-[:HAS_TYPE]->(:TransactionType)
(:Transaction)-[:HAS_LABEL]->(:FraudLabel)
```

## Tool Coverage

- Cypher Template: repeated fraud destinations and account neighborhood investigation.
- Text2Cypher: flexible natural-language questions over the graph schema.
- Optional Similarity Search: similar fraud case lookup over `Transaction.riskText` if embeddings are enabled.

## Screenshots To Capture

1. Aura console graph visualization showing `Account`, `Transaction`, `TransactionType`, and `FraudLabel` nodes.
2. Aura Agent answering: `Find destination accounts connected to repeated fraud transfers and explain the pattern.`

## Optional Link

Not published yet. The current build is Aura Agent-ready and can be published after the Aura console import is complete.
