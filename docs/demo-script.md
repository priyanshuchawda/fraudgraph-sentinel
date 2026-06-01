# FraudGraph Sentinel Demo Script

Target length: 60-90 seconds.

## 1. Open With The Problem

```text
Flat fraud models can flag suspicious transactions, but they do not explain the connected money movement pattern. FraudGraph Sentinel turns synthetic transaction fraud data into a Neo4j knowledge graph and lets an Aura Agent reason over the relationships.
```

## 2. Show The Graph

In Aura Console, show the schema or graph visualization:

```text
The graph connects accounts to transactions and transaction types. Each transaction has a source account, destination account, fraud label, amount, and risk summary.
```

Verified stats to mention:

- 37,585 nodes
- 52,852 relationships
- 13,213 transactions
- 8,213 fraud transactions
- safely under the AuraDB Free target
- optional risk layer: 800 email samples, 400 URL samples, and 12 shared risk indicators

## 3. Ask A Relationship-Based Question

Ask:

```text
Which destination accounts received multiple fraudulent transfers?
```

Expected response:

```text
The agent should use the repeated_fraud_destinations Cypher Template and return destination accounts ranked by fraud count and total fraud amount.
```

## 4. Ask A Path Question

Ask:

```text
Create a fraud investigation brief for destination account C668046170.
```

Expected response:

```text
The agent should turn the repeated-destination finding into a case brief with fraud count, total fraud amount, source accounts, transaction types, risk indicators, and a synthetic-data caveat.
```

## 5. Ask A Path Question

Ask:

```text
Show the highest-value suspicious fraud paths.
```

Expected response:

```text
The agent should return source account, transaction, destination account, transaction type, amount, and risk summary.
```

## 6. Ask A Comparison Question

Ask:

```text
Compare fraudulent TRANSFER and CASH_OUT activity.
```

Expected response:

```text
The agent should compare fraud counts, source accounts, destination accounts, total fraud amount, and average fraud amount by transaction type.
```

## 7. Close

Optional risk-layer question:

```text
Where does PaymentKeywordSignal appear in the graph?
```

Expected response:

```text
The agent should show separate synthetic URLs, emails, or transactions linked by a shared risk indicator without claiming causality.
```

```text
The submission demonstrates a low-cost AuraDB Free graph agent that reasons over fraud context, not just row-level labels. It uses Cypher Templates for trusted investigation paths and Text2Cypher for safe read-only exploration.
```
