from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from fraudgraph_sentinel.aura_config import REQUIRED_NEO4J_ENV, merged_env


@dataclass(frozen=True)
class Check:
    name: str
    command: list[str]
    log_name: str
    requires_env: bool = False


def required_env_present(env: dict[str, str]) -> bool:
    return all(env.get(key) for key in REQUIRED_NEO4J_ENV)


def format_result_line(status: str, command: str, seconds: float, log_path: str) -> str:
    return f"{status} | {command} | {seconds:.2f}s | log={log_path}"


def subprocess_env(base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if base_env is None else base_env)
    src_path = str((Path.cwd() / "src").resolve())
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path if not pythonpath else f"{src_path}{os.pathsep}{pythonpath}"
    )
    return env


def build_checks() -> list[Check]:
    python = sys.executable
    return [
        Check("pytest -q", [python, "-m", "pytest", "-q"], "pytest.log"),
        Check(
            "manifest free-tier verification",
            [
                python,
                "-c",
                (
                    "import json, pathlib; "
                    "m=json.loads(pathlib.Path('outputs/fraudgraph_sentinel/manifest.json').read_text()); "
                    "assert m['fitsConservativeAuraFree'] is True; "
                    "assert m['nodes'] <= 50000; "
                    "assert m['relationships'] <= 175000; "
                    "print(json.dumps({'nodes': m['nodes'], 'relationships': m['relationships'], 'safe': m['fitsConservativeAuraFree']}))"
                ),
            ],
            "manifest.log",
        ),
        Check(
            "agent tool JSON validation",
            [
                python,
                "-c",
                (
                    "import json, pathlib; "
                    "tools=json.loads(pathlib.Path('outputs/fraudgraph_sentinel/agent_tools.json').read_text()); "
                    "assert any(t['type']=='cypher_template' for t in tools); "
                    "assert any(t['type']=='text2cypher' for t in tools); "
                    "print(json.dumps({'tools': len(tools)}))"
                ),
            ],
            "agent-tools.log",
        ),
        Check(
            "Aura Agent import JSON validation",
            [
                python,
                "-c",
                (
                    "import json, pathlib; "
                    "config=json.loads(pathlib.Path('outputs/fraudgraph_sentinel/aura_agent_import_config.json').read_text()); "
                    "assert config['name'] == 'FraudGraph Sentinel'; "
                    "assert config['is_private'] is True; "
                    "assert config['is_mcp_enabled'] is False; "
                    "assert any(t['type']=='cypher_template' for t in config['tools']); "
                    "assert any(t['type']=='text2cypher' for t in config['tools']); "
                    "print(json.dumps({'tools': len(config['tools']), 'private': config['is_private']}))"
                ),
            ],
            "agent-import-config.log",
        ),
        Check(
            "AuraDB connectivity smoke",
            [
                python,
                "-m",
                "fraudgraph_sentinel.aura_cli",
                "--env-file",
                ".env",
                "connect",
            ],
            "aura-connect.log",
            requires_env=True,
        ),
        Check(
            "AuraDB graph verification",
            [
                python,
                "-m",
                "fraudgraph_sentinel.aura_cli",
                "--env-file",
                ".env",
                "verify",
            ],
            "aura-verify.log",
            requires_env=True,
        ),
        Check(
            "AuraDB query verification",
            [
                python,
                "-m",
                "fraudgraph_sentinel.aura_cli",
                "--env-file",
                ".env",
                "query-check",
            ],
            "aura-query-check.log",
            requires_env=True,
        ),
    ]


def run_check(check: Check, log_dir: Path, env: dict[str, str]) -> bool:
    log_path = log_dir / check.log_name
    if check.requires_env and not required_env_present(env):
        print(f"SKIP | {check.name} | missing required environment variable")
        log_path.write_text(
            "SKIP: missing required environment variable\n", encoding="utf-8"
        )
        return True

    start = time.perf_counter()
    completed = subprocess.run(
        check.command,
        cwd=Path.cwd(),
        env=subprocess_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    seconds = time.perf_counter() - start
    log_path.write_text(completed.stdout, encoding="utf-8")
    status = "PASS" if completed.returncode == 0 else "FAIL"
    print(format_result_line(status, check.name, seconds, str(log_path)))
    if completed.returncode != 0:
        lines = [line for line in completed.stdout.splitlines() if line.strip()]
        print("Relevant final lines:")
        for line in lines[-12:]:
            print(line)
    return completed.returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run compact FraudGraph Sentinel validation checks."
    )
    parser.add_argument(
        "--run-id", default=datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    )
    args = parser.parse_args(argv)

    log_dir = Path("artifacts") / "validation" / args.run_id
    log_dir.mkdir(parents=True, exist_ok=True)
    env = merged_env(".env")
    ok = True
    for check in build_checks():
        ok = run_check(check, log_dir, env) and ok
    summary = {"runId": args.run_id, "result": "PASS" if ok else "FAIL"}
    (log_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"RUN_ID={args.run_id}")
    print(f"RESULT={'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
