from fraudgraph_sentinel.agent_tools import build_agent_tool_specs


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
        "fraud_type_comparison",
        "fraud_concentration",
    }.issubset(names)
    assert "Similar fraud case search" in names


def test_text2cypher_spec_blocks_write_and_admin_queries():
    specs = build_agent_tool_specs()
    text2cypher = next(spec for spec in specs if spec["type"] == "text2cypher")

    instructions = str(text2cypher["instructions"]).upper()

    for forbidden in ["CREATE", "MERGE", "DELETE", "DETACH DELETE", "SET", "REMOVE", "DROP", "LOAD CSV"]:
        assert forbidden in instructions
