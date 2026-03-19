from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import paramiko
import psutil
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import NodeConfig, get_settings
from app.models import Node, NodeLog, TaskRecord, TokenUsageRecord

ALLOWED_ACTIONS = {"health_check", "fetch_logs", "check_process"}
TOKEN_PATTERNS = {
    "prompt": re.compile(r'(?:prompt_tokens|input_tokens)[=:" ]+(\d+)', re.IGNORECASE),
    "completion": re.compile(r'(?:completion_tokens|output_tokens)[=:" ]+(\d+)', re.IGNORECASE),
    "total": re.compile(r'total_tokens[=:" ]+(\d+)', re.IGNORECASE),
    "provider": re.compile(r'provider[=:" ]+([a-zA-Z0-9_.-]+)', re.IGNORECASE),
    "model": re.compile(r'(?:model|model_name)[=:" ]+([a-zA-Z0-9_.:-]+)', re.IGNORECASE),
}
logger = logging.getLogger("openclaw.console.probe")


class ProbeError(RuntimeError):
    pass


def tail_local_log(path: str | None, lines: int = 20) -> list[str]:
    if not path:
        return []
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()[-lines:]
    except OSError:
        return []


def summarize_logs(path: str | None) -> str:
    log_lines = tail_local_log(path, lines=5)
    if not path:
        return "no log path configured"
    if log_lines:
        return "\n".join(log_lines).strip() or "log file empty"
    return f"log unavailable: {path}"


def extract_token_usage(lines: list[str]) -> list[dict[str, int | str]]:
    records: list[dict[str, int | str]] = []
    for line in lines:
        prompt_match = TOKEN_PATTERNS["prompt"].search(line)
        completion_match = TOKEN_PATTERNS["completion"].search(line)
        total_match = TOKEN_PATTERNS["total"].search(line)
        if not any([prompt_match, completion_match, total_match]):
            continue
        prompt_tokens = int(prompt_match.group(1)) if prompt_match else 0
        completion_tokens = int(completion_match.group(1)) if completion_match else 0
        total_tokens = int(total_match.group(1)) if total_match else prompt_tokens + completion_tokens
        provider_match = TOKEN_PATTERNS["provider"].search(line)
        model_match = TOKEN_PATTERNS["model"].search(line)
        records.append(
            {
                "provider": provider_match.group(1) if provider_match else "unknown",
                "model_name": model_match.group(1) if model_match else "unknown",
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "raw_line": line[-1000:],
            }
        )
    return records


def persist_token_usage(db: Session, node: Node, entries: list[dict[str, int | str]]) -> int:
    total = 0
    existing_raw_lines = set(
        db.scalars(
            select(TokenUsageRecord.raw_line)
            .where(TokenUsageRecord.node_id == node.id)
            .order_by(TokenUsageRecord.recorded_at.desc())
            .limit(50)
        ).all()
    )
    for entry in entries:
        raw_line = str(entry.get("raw_line") or "")
        total += int(entry.get("total_tokens") or 0)
        if raw_line in existing_raw_lines:
            continue
        db.add(
            TokenUsageRecord(
                node_id=node.id,
                provider=str(entry.get("provider") or "unknown"),
                model_name=str(entry.get("model_name") or "unknown"),
                prompt_tokens=int(entry.get("prompt_tokens") or 0),
                completion_tokens=int(entry.get("completion_tokens") or 0),
                total_tokens=int(entry.get("total_tokens") or 0),
                source="log",
                raw_line=raw_line,
                recorded_at=datetime.now(timezone.utc),
            )
        )
    return total


def _build_windows_probe_script(node: NodeConfig) -> str:
    log_path = (node.log_path or "").replace("'", "''")
    process_name = node.openclaw_process_name.replace("'", "''")
    return rf"""
$cpu = (Get-Counter "\\Processor(_Total)\\% Processor Time").CounterSamples.CookedValue
$os = Get-CimInstance Win32_OperatingSystem
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$proc = Get-Process -Name '{process_name}' -ErrorAction SilentlyContinue
$logTail = @()
if ('{log_path}' -ne '' -and (Test-Path '{log_path}')) {{
  $logTail = Get-Content -Path '{log_path}' -Tail 20
}}
$result = @{{
hostname=$env:COMPUTERNAME
cpu=[Math]::Round($cpu,2)
memory=[Math]::Round((($os.TotalVisibleMemorySize-$os.FreePhysicalMemory)/$os.TotalVisibleMemorySize)*100,2)
disk=[Math]::Round((($disk.Size-$disk.FreeSpace)/$disk.Size)*100,2)
process_exists=([bool]$proc)
checked_at=(Get-Date).ToString('o')
listening_state=if($proc){{'active'}}else{{'idle'}}
log_tail=$logTail
}}
$result | ConvertTo-Json -Compress
""".strip()


def _run_ssh_probe(node: NodeConfig) -> dict:
    settings = get_settings()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    script = _build_windows_probe_script(node)
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
        payload = json.loads(out)
        if isinstance(payload.get("log_tail"), str):
            payload["log_tail"] = [payload["log_tail"]]
        return payload
    except Exception as exc:
        raise ProbeError(f"ssh probe failed: {exc}") from exc
    finally:
        client.close()


def _run_local_probe(node: NodeConfig) -> dict:
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    proc_exists = any(node.openclaw_process_name.lower() in (p.info.get("name", "").lower()) for p in psutil.process_iter(["name"]))
    log_lines = tail_local_log(node.log_path)
    return {
        "hostname": node.host,
        "cpu": round(cpu, 2),
        "memory": round(mem, 2),
        "disk": round(disk, 2),
        "process_exists": proc_exists,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "listening_state": "active" if proc_exists else "idle",
        "log_tail": log_lines,
    }


def run_probe(db: Session, node: Node, cfg: NodeConfig) -> Node:
    now = datetime.now(timezone.utc)
    task = TaskRecord(node_id=node.id, task_type="health_check", status="running", started_at=now)
    db.add(task)
    db.flush()
    try:
        data = _run_local_probe(cfg) if cfg.os_type == "mac" else _run_ssh_probe(cfg)
        log_lines = [str(item) for item in data.get("log_tail", [])]
        summary = "\n".join(log_lines[-5:]).strip() if log_lines else summarize_logs(cfg.log_path)
        token_entries = extract_token_usage(log_lines)
        token_total = persist_token_usage(db, node, token_entries)

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
        node.listening_state = str(data.get("listening_state") or ("active" if data.get("process_exists") else "idle"))
        node.last_log_summary = summary[:2000] if summary else None
        node.last_token_total = token_total
        node.last_error = None
        db.add(NodeLog(node_id=node.id, level="INFO", message=(summary or "probe ok")[:1000]))
        task.status = "success"
        task.result = json.dumps({**data, "token_total": token_total})
    except Exception as exc:
        logger.warning("probe failed for node=%s reason=%s", node.id, exc)
        node.status = "offline"
        node.ssh_status = "error" if cfg.os_type == "windows" else "local"
        node.openclaw_status = "error"
        node.last_probe_at = now
        node.last_failure_at = now
        node.last_error = str(exc)
        node.last_log_summary = None
        node.last_token_total = 0
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
        return {"process_exists": bool(result.get("process_exists")), "listening_state": result.get("listening_state")}
    if action == "fetch_logs":
        if cfg.os_type == "windows":
            result = _run_ssh_probe(cfg)
            return {"summary": "\n".join([str(item) for item in result.get("log_tail", [])][-5:])}
        return {"summary": summarize_logs(cfg.log_path)}
    return {"message": "done"}
