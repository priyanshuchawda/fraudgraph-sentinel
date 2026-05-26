# FraudGraph Sentinel

FraudGraph Sentinel prepares a small, high-signal Neo4j knowledge graph from the synthetic financial fraud dataset. It is designed for Neo4j AuraDB Free, so it keeps every fraud transaction and only a bounded sample of non-fraud rows.

## What It Builds

Graph model:

```text
(:Account)-[:SENT]->(:Transaction)-[:TO]->(:Account)
(:Transaction)-[:HAS_TYPE]->(:TransactionType)
(:Transaction)-[:HAS_LABEL]->(:FraudLabel)
```

The resulting agent can investigate repeated fraud destinations, account neighborhoods, fraud by transaction type, and similar suspicious transaction cases.

## Lowest-Cost Plan

Use AuraDB Free only:

- Create one AuraDB Free instance in the Neo4j Aura Console.
- Keep the import under the conservative free-tier safety target used by this project: 50,000 nodes and 175,000 relationships.
- Do not load the full 6.3M-row CSV into Aura Free.
- Use the generated sample with all fraud rows and 5,000 non-fraud rows.

## Generate Import Files

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m fraudgraph_sentinel.cli `
  --input ".\datasets\cyber_security_fraud_phishing\Synthetic_Financial_datasets_log.csv" `
  --output ".\outputs\fraudgraph_sentinel" `
  --max-non-fraud 5000
```

Outputs:

- `accounts.csv`
- `transactions.csv`
- `transaction_types.csv`
- `fraud_labels.csv`
- `manifest.json`
- `import.cypher`
- `agent_tools.json`

## Load Into Aura

Aura `LOAD CSV` needs the CSV files available over HTTPS. The cheapest practical path is to upload the generated CSVs to a public temporary location you control, such as a GitHub raw file URL or a small static host, then replace `$IMPORT_BASE_URL` in `import.cypher` with that HTTPS folder URL.

Run the Cypher in Aura Query.

## Aura Agent Setup

In the Aura Console:

1. Enable GenAI assistance for the organization.
2. Open the imported database.
3. Create an Aura Agent from the graph.
4. Add the required tools from `agent_tools.json`: the Cypher Template tools and Text2Cypher.
5. Treat the Similarity Search spec as optional. It needs embeddings on `Transaction.riskText`; skip it if you want the zero-cost path.
6. Test with:

```text
Find destination accounts connected to repeated fraud transfers and explain the pattern.
```

## Good Demo Queries

```text
Which transaction type has the highest fraud rate?
```

```text
Find accounts that sent fraud transactions and ended with a zero origin balance.
```

```text
Show me repeated fraud destination accounts and sample origin accounts.
```

```text
Find similar fraud cases to a transfer where the origin balance was completely drained.
```

## Local Tests

```powershell
pytest -q
```
