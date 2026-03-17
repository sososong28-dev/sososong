from __future__ import annotations
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    os_type: Mapped[str] = mapped_column(String(20), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    ip: Mapped[str] = mapped_column(String(100), nullable=False)
    ssh_port: Mapped[int] = mapped_column(Integer, default=22)
    ssh_user: Mapped[str | None] = mapped_column(String(100), nullable=True)
    process_name: Mapped[str] = mapped_column(String(100), default="openclaw")
    log_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="unknown")
    ssh_status: Mapped[str] = mapped_column(String(20), default="unknown")
    openclaw_status: Mapped[str] = mapped_column(String(20), default="unknown")
    process_exists: Mapped[str] = mapped_column(String(5), default="false")
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_probe_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    cpu_usage: Mapped[float | None] = mapped_column(Float, nullable=True)
    memory_usage: Mapped[float | None] = mapped_column(Float, nullable=True)
    disk_usage: Mapped[float | None] = mapped_column(Float, nullable=True)
    listening_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    config_ok: Mapped[str] = mapped_column(String(5), default="true")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    logs: Mapped[list[NodeLog]] = relationship(back_populates="node", cascade="all, delete-orphan")
    tasks: Mapped[list[TaskRecord]] = relationship(back_populates="node", cascade="all, delete-orphan")


class NodeLog(Base):
    __tablename__ = "node_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[str] = mapped_column(ForeignKey("nodes.id"), index=True)
    level: Mapped[str] = mapped_column(String(20), default="INFO")
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    node: Mapped[Node] = relationship(back_populates="logs")


class TaskRecord(Base):
    __tablename__ = "task_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[str] = mapped_column(ForeignKey("nodes.id"), index=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)

    node: Mapped[Node] = relationship(back_populates="tasks")
