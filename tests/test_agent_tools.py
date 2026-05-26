from fraudgraph_sentinel.agent_tools import build_agent_tool_specs


def test_agent_tool_specs_include_required_challenge_tools():
    specs = build_agent_tool_specs()
    tool_types = {spec["type"] for spec in specs}
    names = {spec["name"] for spec in specs}

    assert "cypher_template" in tool_types
    assert "text2cypher" in tool_types
    assert "similarity_search" in tool_types
    assert "Find repeated fraud destinations" in names
    assert "Similar fraud case search" in names
