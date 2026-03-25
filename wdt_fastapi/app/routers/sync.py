from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SyncTask
from ..schemas import APIResponse, SyncTaskOut, TriggerSyncRequest
from ..services.realtime import hub
from ..utils import new_trace_id

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.get("/tasks", response_model=APIResponse[dict])
def list_tasks(db: Session = Depends(get_db)) -> APIResponse[dict]:
    items = db.scalars(select(SyncTask).order_by(SyncTask.id.asc())).all()
    return APIResponse(data={"list": [SyncTaskOut.model_validate(item).model_dump(by_alias=True) for item in items]}, traceId=new_trace_id())


@router.post("/tasks/{task_code}/run", response_model=APIResponse[dict])
async def run_task(task_code: str, db: Session = Depends(get_db)) -> APIResponse[dict]:
    task = db.scalar(select(SyncTask).where(SyncTask.task_code == task_code))
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    task.last_status = "queued"
    task.last_message = "manual trigger accepted"
    task.last_run_time = datetime.now(timezone.utc)
    db.commit()
    await hub.publish("sync.task.triggered", {"taskCode": task_code, "status": "queued"})
    return APIResponse(data={"taskCode": task_code, "status": "queued"}, traceId=new_trace_id())


@router.post("/emit", response_model=APIResponse[dict])
async def emit_event(payload: TriggerSyncRequest) -> APIResponse[dict]:
    await hub.publish(payload.event_type, payload.payload)
    return APIResponse(data={"published": True, "eventType": payload.event_type}, traceId=new_trace_id())
