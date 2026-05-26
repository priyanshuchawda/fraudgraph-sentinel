from fraudgraph_sentinel.risk_enhancement import (
    email_risk_indicators,
    transaction_risk_indicators,
    url_risk_indicators,
)


def test_email_risk_indicators_map_flags_without_claiming_causality():
    row = {
        "label": "phishing",
        "has_link": "1.0",
        "has_attachment": "1.0",
        "urgency_flag": "1.0",
    }

    assert email_risk_indicators(row) == [
        "PhishingEmailLabel",
        "ContainsLink",
        "HasAttachment",
        "UrgentLanguage",
    ]


def test_url_risk_indicators_map_phishing_url_features():
    row = {
        "label": "0",
        "IsHTTPS": "0",
        "HasPasswordField": "1",
        "Bank": "0",
        "Pay": "1",
        "Crypto": "0",
    }

    assert url_risk_indicators(row) == [
        "SuspiciousUrlLabel",
        "InsecureHTTP",
        "PasswordInputSignal",
        "PaymentKeywordSignal",
    ]


def test_transaction_risk_indicators_include_high_amount_and_zeroed_origin():
    row = {
        "transactionId": "tx-1",
        "type": "TRANSFER",
        "amount": "1200000.00",
        "oldBalanceOrigin": "1200000.00",
        "newBalanceOrigin": "0.00",
        "isFraud": "true",
        "destination": "C9",
    }

    assert transaction_risk_indicators(row, repeated_destinations={"C9"}) == [
        "FraudTransaction",
        "HighAmountTransfer",
        "ZeroedOriginBalance",
        "RepeatedFraudDestination",
    ]
