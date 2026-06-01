from fraudgraph_sentinel.agent_tools import (
    build_agent_tool_specs,
    build_aura_agent_import_config,
    infer_aura_parameter_type,
)


def test_agent_tool_specs_include_required_challenge_tools():
    specs = build_agent_tool_specs()
    tool_types = {spec["type"] for spec in specs}
    names = {spec["name"] for spec in specs}

    assert "cypher_template" in tool_types
    assert "text2cypher" in tool_types
    assert "similarity_search" in tool_types
    assert {
        "fraud_overview",
        "repeated_fraud_destinations",
        "high_value_fraud_paths",
        "account_fraud_neighborhood",
        "destination_fraud_profile",
        "fraud_type_comparison",
        "fraud_concentration",
        "risk_indicator_overview",
        "shared_risk_indicator_context",
    }.issubset(names)
    assert "Similar fraud case search" in names


def test_text2cypher_spec_blocks_write_and_admin_queries():
    specs = build_agent_tool_specs()
    text2cypher = next(spec for spec in specs if spec["type"] == "text2cypher")

    instructions = str(text2cypher["instructions"])

    for forbidden in [
        "CREATE",
        "MERGE",
        "DELETE",
        "DETACH DELETE",
        "SET",
        "REMOVE",
        "DROP",
        "LOAD CSV",
    ]:
        assert forbidden in instructions.upper()

    for schema_term in ["RiskIndicator", "EmailSample", "URLSample"]:
        assert schema_term in instructions


def test_aura_agent_import_config_is_private_and_importable():
    config = build_aura_agent_import_config()

    assert config["name"] == "FraudGraph Sentinel"
    assert config["is_private"] is True
    assert config["is_mcp_enabled"] is False
    assert any(tool["type"] == "cypher_template" for tool in config["tools"])
    assert any(tool["type"] == "text2cypher" for tool in config["tools"])


def test_aura_parameter_type_inference_matches_console_options():
    assert infer_aura_parameter_type(True) == "boolean"
    assert infer_aura_parameter_type(1) == "integer"
    assert infer_aura_parameter_type(1.5) == "float"
    assert infer_aura_parameter_type("C123") == "string"
