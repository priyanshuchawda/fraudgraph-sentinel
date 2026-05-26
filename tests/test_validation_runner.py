import os
from pathlib import Path

from fraudgraph_sentinel.validation_runner import (
    format_result_line,
    required_env_present,
    subprocess_env,
)


def test_format_result_line_uses_compact_shape():
    line = format_result_line(
        "PASS", "pytest -q", 1.23, "artifacts/validation/run/pytest.log"
    )

    assert line == "PASS | pytest -q | 1.23s | log=artifacts/validation/run/pytest.log"


def test_required_env_present_checks_only_presence():
    assert required_env_present(
        {
            "NEO4J_URI": "x",
            "NEO4J_USERNAME": "x",
            "NEO4J_PASSWORD": "x",
            "NEO4J_DATABASE": "x",
        }
    )
    assert not required_env_present({"NEO4J_URI": "x", "NEO4J_USERNAME": "x"})


def test_subprocess_env_adds_src_to_pythonpath():
    env = subprocess_env({})
    entries = env["PYTHONPATH"].split(os.pathsep)

    assert str((Path.cwd() / "src").resolve()) in entries
