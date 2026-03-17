from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import NodeConfig, get_settings, load_nodes
from app.database import Base, engine, get_db
from app.models import Node, TaskRecord
from app.probe import execute_action, run_probe
from app.schemas import ActionRequest, NodeBase, NodeDetail, TaskRecordOut

settings = get_settings()
NODE_CFGS: dict[str, NodeConfig] = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    sync_nodes()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


def sync_nodes() -> None:
    cfg_nodes = load_nodes(settings.nodes_config_path)
    global NODE_CFGS
    NODE_CFGS = {n.id: n for n in cfg_nodes}
    from app.database import SessionLocal

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
        db.commit()
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "refresh_seconds": settings.refresh_seconds})


@app.get("/nodes/{node_id}", response_class=HTMLResponse)
def node_page(request: Request, node_id: str):
    return templates.TemplateResponse("node_detail.html", {"request": request, "node_id": node_id})


@app.get("/tasks", response_class=HTMLResponse)
def tasks_page(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request})


@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.get("/api/nodes", response_model=list[NodeBase])
def list_nodes(db: Session = Depends(get_db)):
    nodes = db.scalars(select(Node).order_by(Node.name)).all()
    return nodes


@app.get("/api/nodes/{node_id}", response_model=NodeDetail)
def node_detail(node_id: str, db: Session = Depends(get_db)):
    node = db.scalar(
        select(Node)
        .where(Node.id == node_id)
        .options(selectinload(Node.logs), selectinload(Node.tasks))
    )
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    node.logs = sorted(node.logs, key=lambda l: l.created_at, reverse=True)[:10]
    node.tasks = sorted(node.tasks, key=lambda t: t.started_at, reverse=True)[:10]
    return node


@app.get("/api/tasks", response_model=list[TaskRecordOut])
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.scalars(select(TaskRecord).order_by(TaskRecord.started_at.desc()).limit(100)).all()
    return tasks


@app.post("/api/nodes/{node_id}/check", response_model=NodeBase)
def check_node(node_id: str, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node or node_id not in NODE_CFGS:
        raise HTTPException(status_code=404, detail="node not found")
    return run_probe(db, node, NODE_CFGS[node_id])


@app.post("/api/nodes/{node_id}/action")
def node_action(node_id: str, payload: ActionRequest, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node or node_id not in NODE_CFGS:
        raise HTTPException(status_code=404, detail="node not found")
    try:
        return execute_action(db, node, NODE_CFGS[node_id], payload.action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
