CREATE CONSTRAINT account_id IF NOT EXISTS FOR (a:Account) REQUIRE a.accountId IS UNIQUE;
CREATE CONSTRAINT transaction_id IF NOT EXISTS FOR (t:Transaction) REQUIRE t.transactionId IS UNIQUE;
CREATE CONSTRAINT transaction_type_name IF NOT EXISTS FOR (t:TransactionType) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT fraud_label_name IF NOT EXISTS FOR (l:FraudLabel) REQUIRE l.name IS UNIQUE;
CREATE VECTOR INDEX transaction_risk_text IF NOT EXISTS
FOR (t:Transaction) ON (t.embedding)
OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}};

LOAD CSV WITH HEADERS FROM '$IMPORT_BASE_URL/accounts.csv' AS row
MERGE (:Account {accountId: row.accountId});

LOAD CSV WITH HEADERS FROM '$IMPORT_BASE_URL/transaction_types.csv' AS row
MERGE (:TransactionType {name: row.name});

LOAD CSV WITH HEADERS FROM '$IMPORT_BASE_URL/fraud_labels.csv' AS row
MERGE (:FraudLabel {name: row.name});

LOAD CSV WITH HEADERS FROM '$IMPORT_BASE_URL/transactions.csv' AS row
MERGE (tx:Transaction {transactionId: row.transactionId})
SET tx.step = toInteger(row.step),
    tx.amount = toFloat(row.amount),
    tx.oldBalanceOrigin = toFloat(row.oldBalanceOrigin),
    tx.newBalanceOrigin = toFloat(row.newBalanceOrigin),
    tx.oldBalanceDestination = toFloat(row.oldBalanceDestination),
    tx.newBalanceDestination = toFloat(row.newBalanceDestination),
    tx.isFraud = row.isFraud = 'true',
    tx.isFlaggedFraud = row.isFlaggedFraud = 'true',
    tx.riskText = row.riskText
WITH tx, row
MATCH (origin:Account {accountId: row.origin})
MATCH (destination:Account {accountId: row.destination})
MATCH (kind:TransactionType {name: row.type})
MATCH (label:FraudLabel {name: row.fraudLabel})
MERGE (origin)-[:SENT]->(tx)
MERGE (tx)-[:TO]->(destination)
MERGE (tx)-[:HAS_TYPE]->(kind)
MERGE (tx)-[:HAS_LABEL]->(label);
