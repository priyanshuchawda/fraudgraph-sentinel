from __future__ import annotations

import re
from dataclasses import dataclass

FORBIDDEN_CYPHER_WORDS = (
    "CREATE",
    "MERGE",
    "DELETE",
    "DETACH",
    "SET",
    "REMOVE",
    "DROP",
    "LOAD CSV",
    "CALL DBMS",
    "CALL DB.",
)


@dataclass(frozen=True)
class QueryTemplate:
    name: str
    description: str
    cypher: str
    parameters: dict[str, object]
    example_questions: tuple[str, ...]
    expected_output: str


def assert_read_only_cypher(cypher: str) -> None:
    normalized = re.sub(r"\s+", " ", cypher.upper())
    for word in FORBIDDEN_CYPHER_WORDS:
        if word in normalized:
            raise ValueError(
                f"Cypher template contains forbidden write/admin operation: {word}"
            )


CORE_QUERY_TEMPLATES = (
    QueryTemplate(
        name="fraud_overview",
        description="Summarize fraud count, amount, and transaction-type breakdown.",
        parameters={"limit": 10},
        cypher="""
MATCH (tx:Transaction {isFraud: true})-[:HAS_TYPE]->(kind:TransactionType)
RETURN kind.name AS transactionType,
       count(tx) AS fraudTransactions,
       round(sum(tx.amount), 2) AS totalFraudAmount,
       round(avg(tx.amount), 2) AS averageFraudAmount
ORDER BY fraudTransactions DESC
LIMIT $limit
""",
        example_questions=(
            "What is the fraud overview?",
            "Which transaction types account for fraud?",
            "Summarize fraud amount by type.",
        ),
        expected_output="Fraud transaction counts and amounts grouped by type.",
    ),
    QueryTemplate(
        name="repeated_fraud_destinations",
        description="Find destination accounts receiving repeated fraudulent transactions.",
        parameters={"minFraudTransactions": 2, "limit": 10},
        cypher="""
MATCH (origin:Account)-[:SENT]->(tx:Transaction {isFraud: true})-[:TO]->(dest:Account)
WITH dest, count(tx) AS fraudTransactions, sum(tx.amount) AS totalFraudAmount,
     collect(DISTINCT origin.accountId)[0..5] AS sampleOriginAccounts
WHERE fraudTransactions >= $minFraudTransactions
RETURN dest.accountId AS destinationAccount,
       fraudTransactions,
       round(totalFraudAmount, 2) AS totalFraudAmount,
       sampleOriginAccounts
ORDER BY fraudTransactions DESC, totalFraudAmount DESC
LIMIT $limit
""",
        example_questions=(
            "Which destination accounts received repeated fraud transfers?",
            "Find repeated fraudulent destinations.",
            "Which accounts are common fraud recipients?",
        ),
        expected_output="Destination accounts ranked by repeated fraud count and amount.",
    ),
    QueryTemplate(
        name="high_value_fraud_paths",
        description="Show highest-value fraudulent movements with source and destination context.",
        parameters={"limit": 10},
        cypher="""
MATCH (origin:Account)-[:SENT]->(tx:Transaction {isFraud: true})-[:TO]->(dest:Account)
MATCH (tx)-[:HAS_TYPE]->(kind:TransactionType)
RETURN origin.accountId AS sourceAccount,
       tx.transactionId AS transactionId,
       dest.accountId AS destinationAccount,
       kind.name AS transactionType,
       round(tx.amount, 2) AS amount,
       tx.isFlaggedFraud AS flaggedByRule,
       tx.riskText AS riskSummary
ORDER BY tx.amount DESC
LIMIT $limit
""",
        example_questions=(
            "Show the highest-value fraud paths.",
            "What are the largest fraudulent movements?",
            "Which source and destination accounts appear in top fraud transactions?",
        ),
        expected_output="Top fraud transaction paths with account and amount context.",
    ),
    QueryTemplate(
        name="account_fraud_neighborhood",
        description="Investigate one account's nearby fraudulent incoming or outgoing transactions.",
        parameters={"accountId": "C840083671", "limit": 25},
        cypher="""
MATCH (account:Account {accountId: $accountId})
MATCH (counterparty:Account)-[:SENT]->(tx:Transaction {isFraud: true})-[:TO]->(other:Account)
WHERE account = counterparty OR account = other
MATCH (tx)-[:HAS_TYPE]->(kind:TransactionType)
RETURN tx.transactionId AS transactionId,
       kind.name AS transactionType,
       counterparty.accountId AS sourceAccount,
       other.accountId AS destinationAccount,
       round(tx.amount, 2) AS amount,
       tx.riskText AS riskSummary
ORDER BY tx.amount DESC
LIMIT $limit
""",
        example_questions=(
            "Explain the suspicious neighborhood around this account.",
            "What fraud transactions touch this account?",
            "Show counterparties for this account's fraud activity.",
        ),
        expected_output="Fraud transactions connected to a specific account and counterparties.",
    ),
    QueryTemplate(
        name="destination_fraud_profile",
        description=(
            "Build an investigation brief for one repeated fraud destination account, "
            "including source accounts, transaction types, amounts, and risk indicators."
        ),
        parameters={"accountId": "C668046170", "limit": 25},
        cypher="""
MATCH (:Account)-[:SENT]->(tx:Transaction {isFraud: true})-[:TO]->(dest:Account {accountId: $accountId})
MATCH (tx)-[:HAS_TYPE]->(kind:TransactionType)
OPTIONAL MATCH (tx)-[:HAS_RISK_INDICATOR]->(indicator:RiskIndicator)
WITH dest,
     tx,
     kind,
     collect(DISTINCT indicator.name) AS riskIndicators
ORDER BY tx.amount DESC
WITH dest,
     collect({
       transactionId: tx.transactionId,
       transactionType: kind.name,
       amount: round(tx.amount, 2),
       flaggedByRule: tx.isFlaggedFraud,
       riskSummary: tx.riskText,
       riskIndicators: riskIndicators
     })[0..$limit] AS transactions,
     count(tx) AS fraudTransactions,
     sum(tx.amount) AS totalFraudAmount,
     collect(DISTINCT kind.name) AS transactionTypes
MATCH (origin:Account)-[:SENT]->(fraudTx:Transaction {isFraud: true})-[:TO]->(dest)
WITH dest,
     fraudTransactions,
     totalFraudAmount,
     transactionTypes,
     transactions,
     collect(DISTINCT origin.accountId)[0..10] AS sourceAccounts
RETURN dest.accountId AS destinationAccount,
       fraudTransactions,
       round(totalFraudAmount, 2) AS totalFraudAmount,
       transactionTypes,
       sourceAccounts,
       transactions,
       CASE
         WHEN fraudTransactions >= 2 THEN 'Suspicious repeated destination: this account received multiple fraudulent transactions from different source accounts in the synthetic graph.'
         ELSE 'Fraud-linked destination: this account received at least one fraudulent transaction in the synthetic graph.'
       END AS investigationSummary
""",
        example_questions=(
            "Create a fraud investigation brief for destination account C668046170.",
            "Why is C668046170 suspicious?",
            "Profile this repeated fraud destination account.",
        ),
        expected_output="Case-style destination account brief with fraud totals, sources, transaction details, and risk indicators.",
    ),
    QueryTemplate(
        name="fraud_type_comparison",
        description="Compare fraudulent TRANSFER and CASH_OUT activity patterns.",
        parameters={"limit": 10},
        cypher="""
MATCH (origin:Account)-[:SENT]->(tx:Transaction {isFraud: true})-[:TO]->(dest:Account)
MATCH (tx)-[:HAS_TYPE]->(kind:TransactionType)
RETURN kind.name AS transactionType,
       count(tx) AS fraudTransactions,
       count(DISTINCT origin) AS sourceAccounts,
       count(DISTINCT dest) AS destinationAccounts,
       round(sum(tx.amount), 2) AS totalFraudAmount,
       round(avg(tx.amount), 2) AS averageFraudAmount
ORDER BY fraudTransactions DESC
LIMIT $limit
""",
        example_questions=(
            "Compare fraudulent transfer and cash-out activity.",
            "How do fraud types differ by account involvement?",
            "Which fraud type has the larger total amount?",
        ),
        expected_output="Fraud count, account involvement, and amount by transaction type.",
    ),
    QueryTemplate(
        name="fraud_concentration",
        description="Identify accounts with concentrated fraud exposure by received amount and repeat count.",
        parameters={"limit": 10},
        cypher="""
MATCH (:Account)-[:SENT]->(tx:Transaction {isFraud: true})-[:TO]->(dest:Account)
WITH dest, count(tx) AS fraudTransactions, sum(tx.amount) AS totalFraudAmount, avg(tx.amount) AS averageFraudAmount
RETURN dest.accountId AS destinationAccount,
       fraudTransactions,
       round(totalFraudAmount, 2) AS totalFraudAmount,
       round(averageFraudAmount, 2) AS averageFraudAmount
ORDER BY totalFraudAmount DESC, fraudTransactions DESC
LIMIT $limit
""",
        example_questions=(
            "Where is fraud amount most concentrated?",
            "Which destination accounts received the highest fraud total?",
            "Find concentrated fraud exposure.",
        ),
        expected_output="Destination accounts ranked by total fraud amount.",
    ),
    QueryTemplate(
        name="risk_indicator_overview",
        description="Summarize optional risk indicators across transactions, email samples, and URL samples.",
        parameters={"limit": 20},
        cypher="""
MATCH (item)-[:HAS_RISK_INDICATOR]->(indicator:RiskIndicator)
WITH indicator, labels(item) AS labels
UNWIND labels AS label
RETURN indicator.name AS riskIndicator,
       label AS sampleType,
       count(*) AS linkedItems
ORDER BY riskIndicator ASC, linkedItems DESC
LIMIT $limit
""",
        example_questions=(
            "Summarize the risk indicators across the cyber graph.",
            "Which risk indicators appear across transactions, emails, and URLs?",
            "Show optional ScamChain risk indicator coverage.",
        ),
        expected_output="Risk indicators grouped by linked graph entity label.",
    ),
    QueryTemplate(
        name="shared_risk_indicator_context",
        description="Show how one risk indicator appears across separate synthetic datasets without claiming causality.",
        parameters={"indicator": "PaymentKeywordSignal", "limit": 10},
        cypher="""
MATCH (item)-[:HAS_RISK_INDICATOR]->(indicator:RiskIndicator {name: $indicator})
RETURN indicator.name AS riskIndicator,
       labels(item) AS itemLabels,
       coalesce(item.transactionId, item.emailId, item.urlId) AS itemId,
       coalesce(item.riskText, item.subject, item.domain) AS context
LIMIT $limit
""",
        example_questions=(
            "Where does PaymentKeywordSignal appear in the graph?",
            "Show shared risk context across datasets.",
            "Which graph entities share this risk indicator?",
        ),
        expected_output="Separate synthetic graph entities connected to a chosen risk indicator.",
    ),
)

for template in CORE_QUERY_TEMPLATES:
    assert_read_only_cypher(template.cypher)
