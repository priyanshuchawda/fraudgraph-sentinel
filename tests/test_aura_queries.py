from fraudgraph_sentinel.aura_queries import (
    CORE_QUERY_TEMPLATES,
    assert_read_only_cypher,
)


def test_core_query_templates_are_read_only_and_named():
    names = {template.name for template in CORE_QUERY_TEMPLATES}

    assert {
        "fraud_overview",
        "repeated_fraud_destinations",
        "high_value_fraud_paths",
        "account_fraud_neighborhood",
        "fraud_type_comparison",
        "fraud_concentration",
        "risk_indicator_overview",
        "shared_risk_indicator_context",
    }.issubset(names)
    for template in CORE_QUERY_TEMPLATES:
        assert_read_only_cypher(template.cypher)
        assert template.description
        assert template.example_questions


def test_read_only_guard_rejects_write_or_admin_cypher():
    for cypher in [
        "CREATE (n)",
        "MATCH (n) DELETE n",
        "LOAD CSV FROM 'x' AS row RETURN row",
    ]:
        try:
            assert_read_only_cypher(cypher)
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"Expected write/admin Cypher to be rejected: {cypher}"
            )
