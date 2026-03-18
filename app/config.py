from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class NodeConfig(BaseModel):
    id: str
    name: str
    os_type: Literal["mac", "windows"]
    host: str
    ip: str
    ssh_port: int = 22
    ssh_user: str | None = None
    openclaw_process_name: str = "openclaw"
    log_path: str | None = None


class Settings(BaseSettings):
    app_name: str = "OpenClaw Control Center"
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "sqlite:///./data.db"
    nodes_config_path: str = "config/nodes.yaml"
    refresh_seconds: int = 15
    probe_interval_seconds: int = 60
    ssh_timeout_seconds: int = 10
    api_token: str = "change-me"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("nodes_config_path")
    @classmethod
    def normalize_nodes_config_path(cls, value: str) -> str:
        return str(Path(value).expanduser().resolve())


class NodeFile(BaseModel):
    nodes: list[NodeConfig] = Field(default_factory=list)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_nodes(path: str) -> list[NodeConfig]:
    config_path = Path(path)
    if not config_path.exists():
        return []
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    node_file = NodeFile.model_validate(data)
    return node_file.nodes
