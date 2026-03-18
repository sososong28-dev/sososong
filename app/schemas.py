from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel


class NodeBase(BaseModel):
    id: str
    name: str
    os_type: str
    host: str
    ip: str
    status: str
    ssh_status: str
    openclaw_status: str
    process_exists: str
    last_heartbeat_at: Optional[datetime]
    last_success_at: Optional[datetime]
    last_probe_at: Optional[datetime]
    last_failure_at: Optional[datetime]
    last_error: Optional[str]
    cpu_usage: Optional[float]
    memory_usage: Optional[float]
    disk_usage: Optional[float]
    listening_state: Optional[str]

    class Config:
        from_attributes = True


class NodeLogOut(BaseModel):
    level: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskRecordOut(BaseModel):
    id: int
    node_id: str
    task_type: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    error_message: Optional[str]
    result: Optional[str]

    class Config:
        from_attributes = True


class NodeDetail(NodeBase):
    logs: List[NodeLogOut]
    tasks: List[TaskRecordOut]


class ActionRequest(BaseModel):
    action: Literal["health_check", "fetch_logs", "check_process", "run_command"]


class CommandResult(BaseModel):
    command: str
    exit_code: int
    stdout: str
    stderr: str
    success: bool
