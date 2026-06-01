from fraudgraph_sentinel import aura_cli
from fraudgraph_sentinel.aura_config import Neo4jConfig


class FakeDriver:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_connect_failure_reports_safe_message_without_uri(
    monkeypatch, tmp_path, capsys
):
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")
    driver = FakeDriver()

    monkeypatch.setattr(
        aura_cli,
        "load_neo4j_config",
        lambda _path: Neo4jConfig(
            uri="neo4j+s://secret-host.databases.neo4j.io",
            username="neo4j",
            password="secret",
            database="neo4j",
        ),
    )
    monkeypatch.setattr(aura_cli, "get_driver", lambda _config: driver)
    monkeypatch.setattr(
        aura_cli,
        "smoke_test",
        lambda _driver, _config: (_ for _ in ()).throw(
            ValueError("Cannot resolve address secret-host.databases.neo4j.io:7687")
        ),
    )

    exit_code = aura_cli.main(["--env-file", str(env_file), "connect"])
    output = capsys.readouterr().out

    assert exit_code == 2
    assert "AuraDB connectivity: FAIL" in output
    assert "database appears paused, deleted, or unreachable" in output
    assert "secret-host" not in output
    assert "neo4j+s://" not in output
    assert driver.closed
