from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import paramiko
import psutil
from sqlalchemy.orm import Session

from app.config import NodeConfig, get_settings
from app.models import Node, NodeLog, TaskRecord

ALLOWED_ACTIONS = {"health_check", "fetch_logs", "check_process"}
logger = logging.getLogger("openclaw.console.probe")


class ProbeError(RuntimeError):
    pass


def summarize_logs(path: str | None) -> str:
    if not path:
        return "no log path configured"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.readlines()[-5:]
        return "".join(lines).strip() or "log file empty"
    except OSError as exc:
        return f"log unavailable: {exc}"


def _run_ssh_probe(node: NodeConfig) -> dict:
    settings = get_settings()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    script = rf"""
$cpu = (Get-Counter "\\Processor(_Total)\\% Processor Time").CounterSamples.CookedValue
$os = Get-CimInstance Win32_OperatingSystem
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$proc = Get-Process -Name "{node.openclaw_process_name}" -ErrorAction SilentlyContinue
$result = @{{
hostname=$env:COMPUTERNAME
cpu=[Math]::Round($cpu,2)
memory=[Math]::Round((($os.TotalVisibleMemorySize-$os.FreePhysicalMemory)/$os.TotalVisibleMemorySize)*100,2)
disk=[Math]::Round((($disk.Size-$disk.FreeSpace)/$disk.Size)*100,2)
process_exists=([bool]$proc)
checked_at=(Get-Date).ToString("o")
}}
$result | ConvertTo-Json -Compress
""".strip()
    try:
        client.connect(
            hostname=node.host,
            port=node.ssh_port,
            username=node.ssh_user,
            timeout=settings.ssh_timeout_seconds,
        )
        _, stdout, stderr = client.exec_command(f'powershell -NoProfile -Command "{script}"')
        out = stdout.read().decode("utf-8", errors="ignore").strip()
        err = stderr.read().decode("utf-8", errors="ignore").strip()
        if err:
            raise ProbeError(err)
        if not out:
            raise ProbeError("empty response from remote node")
        return json.loads(out)
    except Exception as exc:
        raise ProbeError(f"ssh probe failed: {exc}") from exc
    finally:
        client.close()


def _run_local_probe(node: NodeConfig) -> dict:
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    proc_exists = any(node.openclaw_process_name.lower() in (p.info.get("name", "").lower()) for p in psutil.process_iter(["name"]))
    return {
        "hostname": node.host,
        "cpu": round(cpu, 2),
        "memory": round(mem, 2),
        "disk": round(disk, 2),
        "process_exists": proc_exists,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def run_probe(db: Session, node: Node, cfg: NodeConfig) -> Node:
    now = datetime.now(timezone.utc)
    task = TaskRecord(node_id=node.id, task_type="health_check", status="running", started_at=now)
    db.add(task)
    db.flush()
    try:
        data = _run_local_probe(cfg) if cfg.os_type == "mac" else _run_ssh_probe(cfg)
        node.status = "online"
        node.ssh_status = "connected" if cfg.os_type == "windows" else "local"
        node.openclaw_status = "running" if data.get("process_exists") else "stopped"
        node.process_exists = str(bool(data.get("process_exists"))).lower()
        node.last_heartbeat_at = now
        node.last_success_at = now
        node.last_probe_at = now
        node.cpu_usage = data.get("cpu")
        node.memory_usage = data.get("memory")
        node.disk_usage = data.get("disk")
        node.last_error = None
        summary = summarize_logs(cfg.log_path)
        db.add(NodeLog(node_id=node.id, level="INFO", message=summary[:1000]))
        task.status = "success"
        task.result = json.dumps(data)
    except Exception as exc:
        logger.warning("probe failed for node=%s reason=%s", node.id, exc)
        node.status = "offline"
        node.ssh_status = "error" if cfg.os_type == "windows" else "local"
        node.openclaw_status = "error"
        node.last_probe_at = now
        node.last_failure_at = now
        node.last_error = str(exc)
        db.add(NodeLog(node_id=node.id, level="ERROR", message=str(exc)[:1000]))
        task.status = "failed"
        task.error_message = str(exc)
    task.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(node)
    return node


def execute_action(db: Session, node: Node, cfg: NodeConfig, action: str) -> dict:
    if action not in ALLOWED_ACTIONS:
        raise ValueError("action not allowed")
    if action == "health_check":
        run_probe(db, node, cfg)
        return {"message": "health_check completed"}
    if action == "check_process":
        result = _run_local_probe(cfg) if cfg.os_type == "mac" else _run_ssh_probe(cfg)
        return {"process_exists": bool(result.get("process_exists"))}
    if action == "fetch_logs":
        return {"summary": summarize_logs(cfg.log_path)}
    return {"message": "done"}
