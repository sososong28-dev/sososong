from datetime import datetime
from typing import Literal

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
    last_heartbeat_at: datetime | None
    last_success_at: datetime | None
    last_probe_at: datetime | None
    last_failure_at: datetime | None
    last_error: str | None
    cpu_usage: float | None
    memory_usage: float | None
    disk_usage: float | None
    listening_state: str | None

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
    ended_at: datetime | None
    error_message: str | None
    result: str | None

    class Config:
        from_attributes = True


class NodeDetail(NodeBase):
    logs: list[NodeLogOut]
    tasks: list[TaskRecordOut]


class ActionRequest(BaseModel):
    action: Literal["health_check", "fetch_logs", "check_process"]
