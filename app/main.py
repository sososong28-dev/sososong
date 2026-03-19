from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import NodeConfig, get_settings, load_nodes
from app.database import Base, SessionLocal, engine, get_db
from app.models import Node, TaskRecord, TokenUsageRecord
from app.probe import execute_action, run_probe
from app.schemas import ActionRequest, DashboardSummary, NodeBase, NodeDetail, NodesResponse, TaskRecordOut, TokenUsageOut

settings = get_settings()
logger = logging.getLogger("openclaw.console")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
api_key_header = APIKeyHeader(name="X-API-Token", auto_error=False)
NodeId = Annotated[str, Path(pattern=r"^[a-zA-Z0-9-]{3,64}$")]


async def monitor_nodes_periodically() -> None:
    while True:
        db = SessionLocal()
        try:
            for cfg in load_nodes(settings.nodes_config_path):
                node = db.get(Node, cfg.id)
                if node:
                    run_probe(db, node, cfg)
        except Exception as exc:
            logger.warning("background monitor tick failed: %s", exc)
            db.rollback()
        finally:
            db.close()
        await asyncio.sleep(settings.probe_interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    sync_nodes()
    monitor_task = None
    if settings.enable_background_monitor:
        monitor_task = asyncio.create_task(monitor_nodes_periodically())
    app.state.monitor_task = monitor_task
    yield
    if monitor_task:
        monitor_task.cancel()
        with suppress(asyncio.CancelledError):
            await monitor_task


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def get_node_cfg(node_id: str) -> NodeConfig | None:
    cfg_nodes = load_nodes(settings.nodes_config_path)
    cfg_map = {node.id: node for node in cfg_nodes}
    return cfg_map.get(node_id)


def require_api_token(token: str | None = Depends(api_key_header)) -> None:
    if token != settings.api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api token")


def build_dashboard_summary(db: Session) -> DashboardSummary:
    nodes = db.scalars(select(Node)).all()
    total_tokens = db.scalar(select(func.coalesce(func.sum(TokenUsageRecord.total_tokens), 0))) or 0
    return DashboardSummary(
        total_nodes=len(nodes),
        online_nodes=sum(1 for node in nodes if node.status == "online"),
        offline_nodes=sum(1 for node in nodes if node.status == "offline"),
        warning_nodes=sum(1 for node in nodes if node.openclaw_status in {"error", "stopped"}),
        total_tokens=int(total_tokens),
        windows_nodes=sum(1 for node in nodes if node.os_type == "windows"),
    )


def sync_nodes() -> None:
    cfg_nodes = load_nodes(settings.nodes_config_path)
    db = SessionLocal()
    try:
        for cfg in cfg_nodes:
            existing = db.get(Node, cfg.id)
            if not existing:
                db.add(
                    Node(
                        id=cfg.id,
                        name=cfg.name,
                        os_type=cfg.os_type,
                        host=cfg.host,
                        ip=cfg.ip,
                        ssh_port=cfg.ssh_port,
                        ssh_user=cfg.ssh_user,
                        process_name=cfg.openclaw_process_name,
                        log_path=cfg.log_path,
                        status="unknown",
                    )
                )
            else:
                existing.name = cfg.name
                existing.os_type = cfg.os_type
                existing.host = cfg.host
                existing.ip = cfg.ip
                existing.ssh_port = cfg.ssh_port
                existing.ssh_user = cfg.ssh_user
                existing.process_name = cfg.openclaw_process_name
                existing.log_path = cfg.log_path
        db.commit()
    finally:
        db.close()


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "internal server error"})


@app.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "refresh_seconds": settings.refresh_seconds})


@app.get("/nodes/{node_id}", response_class=HTMLResponse)
def node_page(request: Request, node_id: NodeId):
    return templates.TemplateResponse("node_detail.html", {"request": request, "node_id": node_id})


@app.get("/tasks", response_class=HTMLResponse)
def tasks_page(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request})


@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/nodes", response_model=NodesResponse, dependencies=[Depends(require_api_token)])
def list_nodes(db: Session = Depends(get_db)):
    nodes = db.scalars(select(Node).order_by(Node.name)).all()
    return NodesResponse(summary=build_dashboard_summary(db), nodes=nodes)


@app.get("/api/nodes/{node_id}", response_model=NodeDetail, dependencies=[Depends(require_api_token)])
def node_detail(node_id: NodeId, db: Session = Depends(get_db)):
    node = db.scalar(
        select(Node)
        .where(Node.id == node_id)
        .options(selectinload(Node.logs), selectinload(Node.tasks), selectinload(Node.token_usage_records))
    )
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    node.logs = sorted(node.logs, key=lambda l: l.created_at, reverse=True)[:10]
    node.tasks = sorted(node.tasks, key=lambda t: t.started_at, reverse=True)[:10]
    node.token_usage_records = sorted(node.token_usage_records, key=lambda item: item.recorded_at, reverse=True)[:20]
    return node


@app.get("/api/tasks", response_model=list[TaskRecordOut], dependencies=[Depends(require_api_token)])
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.scalars(select(TaskRecord).order_by(TaskRecord.started_at.desc()).limit(100)).all()
    return tasks


@app.get("/api/token-usage", response_model=list[TokenUsageOut], dependencies=[Depends(require_api_token)])
def list_token_usage(db: Session = Depends(get_db)):
    return db.scalars(select(TokenUsageRecord).order_by(TokenUsageRecord.recorded_at.desc()).limit(200)).all()


@app.post("/api/nodes/check-all", response_model=NodesResponse, dependencies=[Depends(require_api_token)])
def check_all_nodes(db: Session = Depends(get_db)):
    for cfg in load_nodes(settings.nodes_config_path):
        node = db.get(Node, cfg.id)
        if node:
            run_probe(db, node, cfg)
    nodes = db.scalars(select(Node).order_by(Node.name)).all()
    return NodesResponse(summary=build_dashboard_summary(db), nodes=nodes)


@app.post("/api/nodes/{node_id}/check", response_model=NodeBase, dependencies=[Depends(require_api_token)])
def check_node(node_id: NodeId, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    cfg = get_node_cfg(node_id)
    if not node or not cfg:
        raise HTTPException(status_code=404, detail="node not found")
    try:
        return run_probe(db, node, cfg)
    except Exception as exc:
        logger.exception("probe failed for node=%s", node_id)
        raise HTTPException(status_code=500, detail=f"probe failed: {exc}") from exc


@app.post("/api/nodes/{node_id}/action", dependencies=[Depends(require_api_token)])
def node_action(node_id: NodeId, payload: ActionRequest, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    cfg = get_node_cfg(node_id)
    if not node or not cfg:
        raise HTTPException(status_code=404, detail="node not found")
    try:
        return execute_action(db, node, cfg, payload.action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("action failed for node=%s action=%s", node_id, payload.action)
        raise HTTPException(status_code=500, detail=f"action failed: {exc}") from exc
