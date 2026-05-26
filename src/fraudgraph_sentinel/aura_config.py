from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REQUIRED_NEO4J_ENV = ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD", "NEO4J_DATABASE")
OPTIONAL_AURA_ENV = (
    "AURA_CLIENT_ID",
    "AURA_CLIENT_SECRET",
    "AURA_INSTANCEID",
    "AURA_INSTANCENAME",
)
VALID_URI_PREFIXES = (
    "neo4j+s://",
    "neo4j+ssc://",
    "bolt+s://",
    "bolt+ssc://",
    "neo4j://",
    "bolt://",
)


@dataclass(frozen=True)
class Neo4jConfig:
    uri: str
    username: str
    password: str
    database: str


def read_env_file(path: Path | str = ".env") -> dict[str, str]:
    env_path = Path(path)
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def merged_env(path: Path | str = ".env") -> dict[str, str]:
    values = dict(os.environ)
    values.update(read_env_file(path))
    return values


def required_env_status(env: dict[str, str]) -> dict[str, str]:
    return {key: "PRESENT" if env.get(key) else "MISSING" for key in REQUIRED_NEO4J_ENV}


def optional_env_status(env: dict[str, str]) -> dict[str, str]:
    return {key: "PRESENT" if env.get(key) else "MISSING" for key in OPTIONAL_AURA_ENV}


def load_neo4j_config(path: Path | str = ".env") -> Neo4jConfig:
    env = merged_env(path)
    missing = [key for key in REQUIRED_NEO4J_ENV if not env.get(key)]
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
    uri = env["NEO4J_URI"]
    if not uri.startswith(VALID_URI_PREFIXES):
        raise ValueError(
            "NEO4J_URI must start with neo4j+s://, neo4j+ssc://, bolt+s://, "
            "bolt+ssc://, neo4j://, or bolt://"
        )
    return Neo4jConfig(
        uri=uri,
        username=env["NEO4J_USERNAME"],
        password=env["NEO4J_PASSWORD"],
        database=env["NEO4J_DATABASE"],
    )
