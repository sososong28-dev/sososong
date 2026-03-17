import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    nodes_path = tmp_path / "nodes.yaml"
    nodes_path.write_text(
        """
nodes:
  - id: mac-openclaw-master
    name: mac-openclaw-master
    os_type: mac
    host: localhost
    ip: 127.0.0.1
    openclaw_process_name: python
  - id: win-openclaw-01
    name: win-openclaw-01
    os_type: windows
    host: 127.0.0.1
    ip: 127.0.0.1
    ssh_user: fake
    openclaw_process_name: openclaw
  - id: win-openclaw-02
    name: win-openclaw-02
    os_type: windows
    host: 127.0.0.1
    ip: 127.0.0.1
    ssh_user: fake
    openclaw_process_name: openclaw
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("NODES_CONFIG_PATH", str(nodes_path))

    from app.config import get_settings

    get_settings.cache_clear()

    import importlib
    import app.database
    import app.main

    importlib.reload(app.database)
    importlib.reload(app.main)

    with TestClient(app.main.app) as c:
        yield c
