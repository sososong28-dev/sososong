from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import paramiko
import psutil
from sqlalchemy.orm import Session

from app.config import NodeConfig, get_settings
from app.models import Node, NodeLog, TaskRecord

ALLOWED_ACTIONS = {"health_check", "fetch_logs", "check_process", "run_command"}
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


def execute_ssh_command(node: NodeConfig, command: str) -> dict:
    """在远程节点执行命令"""
    if node.os_type == "mac":
        # Mac 本地执行
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "exit_code": -1,
                "stdout": "",
                "stderr": "Command timeout",
                "success": False
            }
        except Exception as exc:
            return {
                "command": command,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(exc),
                "success": False
            }
    else:
        # Windows SSH 执行
        settings = get_settings()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        connect_kwargs = {
            "hostname": node.host,
            "port": node.ssh_port,
            "username": node.ssh_user,
            "timeout": settings.ssh_timeout_seconds,
            "allow_agent": False,
            "look_for_keys": False,
        }
        if node.ssh_password:
            connect_kwargs["password"] = node.ssh_password
        
        try:
            client.connect(**connect_kwargs)
            _, stdout, stderr = client.exec_command(command, timeout=30)
            exit_code = stdout.channel.recv_exit_status()
            return {
                "command": command,
                "exit_code": exit_code,
                "stdout": stdout.read().decode("utf-8", errors="ignore").strip(),
                "stderr": stderr.read().decode("utf-8", errors="ignore").strip(),
                "success": exit_code == 0
            }
        except Exception as exc:
            return {
                "command": command,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(exc),
                "success": False
            }
        finally:
            client.close()


def _run_ssh_probe(node: NodeConfig) -> dict:
    settings = get_settings()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # PowerShell 脚本（使用 base64 编码避免编码问题）
    script = f'''
$ProgressPreference = 'SilentlyContinue'
$cpu = (Get-Counter "\\Processor(_Total)\\% Processor Time").CounterSamples.CookedValue
$os = Get-CimInstance Win32_OperatingSystem
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$proc = Get-Process -Name "{node.openclaw_process_name}" -ErrorAction SilentlyContinue
[PSCustomObject]@{{
    hostname = $env:COMPUTERNAME
    cpu = [Math]::Round($cpu, 2)
    memory = [Math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 2)
    disk = [Math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 2)
    process_exists = [bool]$proc
    checked_at = (Get-Date).ToString("o")
}} | ConvertTo-Json -Compress
'''.strip()
    
    # Base64 编码脚本（UTF-16LE 是 PowerShell 的标准编码）
    import base64
    script_bytes = script.encode('utf-16-le')
    script_base64 = base64.b64encode(script_bytes).decode('ascii')
    
    try:
        # 支持密码或密钥认证
        connect_kwargs = {
            "hostname": node.host,
            "port": node.ssh_port,
            "username": node.ssh_user,
            "timeout": settings.ssh_timeout_seconds,
            "allow_agent": False,
            "look_for_keys": False,
        }
        if node.ssh_password:
            connect_kwargs["password"] = node.ssh_password
        
        client.connect(**connect_kwargs)
        # 使用 -EncodedCommand 并禁用进度显示
        _, stdout, stderr = client.exec_command(f'powershell -NoProfile -NonInteractive -EncodedCommand {script_base64} 2>&1')
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
    
    # 检测进程（支持部分匹配）
    process_name = node.openclaw_process_name.lower()
    proc_exists = False
    
    for p in psutil.process_iter(['name', 'cmdline']):
        try:
            # 检查进程名
            p_name = p.info.get('name', '').lower()
            if process_name in p_name:
                proc_exists = True
                break
            # 检查命令行（有些进程名是 python，但实际运行的是 openclaw）
            cmdline = ' '.join(p.info.get('cmdline', []) or []).lower()
            if process_name in cmdline:
                proc_exists = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
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
    if action == "run_command":
        # 执行健康检查命令
        health_results = []
        for cmd in cfg.health_commands:
            result = execute_ssh_command(cfg, cmd)
            health_results.append(result)
        # 执行任务命令（如果有）
        task_results = []
        if hasattr(cfg, 'task_commands') and cfg.task_commands:
            for cmd in cfg.task_commands:
                result = execute_ssh_command(cfg, cmd)
                task_results.append(result)
        return {"commands": health_results + task_results, "health": health_results, "tasks": task_results}
    return {"message": "done"}
