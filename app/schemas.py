from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TokenUsageOut(BaseModel):
    id: int
    node_id: str
    provider: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    source: str
    raw_line: str | None
    recorded_at: datetime

    class Config:
        from_attributes = True


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
    last_log_summary: str | None
    last_token_total: int

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
    token_usage_records: list[TokenUsageOut]


class DashboardSummary(BaseModel):
    total_nodes: int
    online_nodes: int
    offline_nodes: int
    warning_nodes: int
    total_tokens: int
    windows_nodes: int


class NodesResponse(BaseModel):
    summary: DashboardSummary
    nodes: list[NodeBase]


class ActionRequest(BaseModel):
    action: Literal["health_check", "fetch_logs", "check_process"]
