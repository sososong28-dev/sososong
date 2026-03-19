from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    nodes_path = tmp_path / "nodes.yaml"
    log_path = tmp_path / "openclaw.log"
    log_path.write_text(
        '\n'.join(
            [
                'provider=openai model=gpt-4.1 prompt_tokens=120 completion_tokens=30 total_tokens=150',
                'provider=anthropic model=claude-3.7 input_tokens=200 output_tokens=50 total_tokens=250',
            ]
        ),
        encoding='utf-8',
    )
    nodes_path.write_text(
        f"""
nodes:
  - id: mac-openclaw-master
    name: mac-openclaw-master
    os_type: mac
    host: localhost
    ip: 127.0.0.1
    openclaw_process_name: python
    log_path: {log_path}
  - id: win-openclaw-01
    name: win-openclaw-01
    os_type: windows
    host: 127.0.0.1
    ip: 127.0.0.1
    ssh_user: fake
    openclaw_process_name: openclaw
    log_path: C:/OpenClaw/logs/openclaw.log
  - id: win-openclaw-02
    name: win-openclaw-02
    os_type: windows
    host: 127.0.0.1
    ip: 127.0.0.1
    ssh_user: fake
    openclaw_process_name: openclaw
    log_path: C:/OpenClaw/logs/openclaw.log
""",
        encoding='utf-8',
    )
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db_path}')
    monkeypatch.setenv('NODES_CONFIG_PATH', str(nodes_path))
    monkeypatch.setenv('API_TOKEN', 'test-token')
    monkeypatch.setenv('ENABLE_BACKGROUND_MONITOR', 'false')

    from app.config import get_settings

    get_settings.cache_clear()

    import importlib
    import app.database
    import app.main

    importlib.reload(app.database)
    importlib.reload(app.main)

    with TestClient(app.main.app) as c:
        yield c
