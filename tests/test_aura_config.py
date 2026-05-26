import pytest

from fraudgraph_sentinel.aura_config import (
    load_neo4j_config,
    read_env_file,
    required_env_status,
)


def test_required_env_status_reports_presence_without_values():
    env = {
        "NEO4J_URI": "neo4j+s://example.databases.neo4j.io",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "secret",
        "NEO4J_DATABASE": "neo4j",
    }

    status = required_env_status(env)

    assert status == {
        "NEO4J_URI": "PRESENT",
        "NEO4J_USERNAME": "PRESENT",
        "NEO4J_PASSWORD": "PRESENT",
        "NEO4J_DATABASE": "PRESENT",
    }


def test_read_env_file_ignores_comments_and_quotes(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        'NEO4J_URI="neo4j+s://example.databases.neo4j.io"\n# ignored\nNEO4J_USERNAME=neo4j\n',
        encoding="utf-8",
    )

    env = read_env_file(env_file)

    assert env["NEO4J_URI"] == "neo4j+s://example.databases.neo4j.io"
    assert env["NEO4J_USERNAME"] == "neo4j"


def test_load_neo4j_config_rejects_missing_required_values(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "NEO4J_URI=neo4j+s://example.databases.neo4j.io\n", encoding="utf-8"
    )

    with pytest.raises(ValueError) as error:
        load_neo4j_config(env_file)

    assert "NEO4J_USERNAME" in str(error.value)
    assert "NEO4J_PASSWORD" in str(error.value)
    assert "NEO4J_DATABASE" in str(error.value)


def test_load_neo4j_config_rejects_non_neo4j_uri(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "NEO4J_URI=https://example.com",
                "NEO4J_USERNAME=neo4j",
                "NEO4J_PASSWORD=secret",
                "NEO4J_DATABASE=neo4j",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as error:
        load_neo4j_config(env_file)

    assert (
        "NEO4J_URI must start with neo4j+s://, neo4j+ssc://, bolt+s://, bolt+ssc://, neo4j://, or bolt://"
        in str(error.value)
    )
