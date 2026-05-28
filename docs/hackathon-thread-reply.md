# Hackathon Thread Reply

Use this as the submission reply after adding screenshots.

## FraudGraph Sentinel

**Agent Name:** FraudGraph Sentinel

**What it does:** FraudGraph Sentinel is a Neo4j Aura Agent for investigating synthetic cyber-fraud transaction patterns. It reasons over account-to-transaction-to-account paths, repeated fraudulent destinations, high-value fraud movements, fraud-type patterns, account neighborhoods, and shared risk indicators.

**Dataset and why a graph fits:** The project uses a synthetic financial transaction fraud dataset with 6,362,620 source rows. The AuraDB Free graph keeps all 8,213 fraud rows plus a deterministic 5,000-row non-fraud sample. Fraud is relational, so a graph is a better fit than flat rows: it reveals repeated recipients, source-to-transaction-to-destination paths, concentrated fraud exposure, and connected risk signals.

**Graph stats verified in AuraDB:**

- Enhanced nodes: 38,797
- Enhanced relationships: 74,262
- Transaction nodes: 13,213
- Fraud transactions: 8,213
- Conservative AuraDB Free target: below 50,000 nodes and 175,000 relationships

**Agent tools used:**

- Cypher Template
- Text2Cypher

**Prepared Cypher Template tools:**

- `fraud_overview`
- `repeated_fraud_destinations`
- `high_value_fraud_paths`
- `account_fraud_neighborhood`
- `fraud_type_comparison`
- `fraud_concentration`
- `risk_indicator_overview`
- `shared_risk_indicator_context`

**Demo questions:**

- Which destination accounts received multiple fraudulent transfers?
- Compare fraudulent TRANSFER and CASH_OUT activity.
- Show the highest-value suspicious fraud paths.
- Which risk indicators appear across the cyber graph?

**Important note:** The dataset is synthetic. The optional email, URL, and transaction risk layer connects separate datasets through shared risk indicators only; it does not claim a real causal attack chain.

**GitHub repository:** https://github.com/priyanshuchawda/fraudgraph-sentinel

**Screenshots/demo:**

- Aura Console graph screenshot: `[add screenshot]`
- Aura Agent response screenshot or short demo: `[add screenshot/demo link]`

**Agent link:** Not published. The project uses the free/internal Aura Agent path; external publishing was intentionally skipped to avoid paid deployment costs.
