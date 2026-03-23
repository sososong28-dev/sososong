from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ShipmentSyncRecord
from ..schemas import APIResponse, PageData, ShipmentOut
from ..utils import new_trace_id

router = APIRouter(prefix="/api/shipments", tags=["shipments"])


@router.get("", response_model=APIResponse[PageData[ShipmentOut]])
def list_shipments(
    order_no: str | None = Query(default=None, alias="orderNo"),
    ack_status: int | None = Query(default=None, alias="ackStatus"),
    page_no: int = Query(default=1, alias="pageNo", ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=100),
    db: Session = Depends(get_db),
) -> APIResponse[PageData[ShipmentOut]]:
    stmt = select(ShipmentSyncRecord).order_by(ShipmentSyncRecord.id.desc())
    if order_no:
        stmt = stmt.where(ShipmentSyncRecord.order_no == order_no)
    if ack_status is not None:
        stmt = stmt.where(ShipmentSyncRecord.ack_status == ack_status)
    items = db.scalars(stmt.offset((page_no - 1) * page_size).limit(page_size)).all()
    total = len(db.scalars(select(ShipmentSyncRecord)).all())
    page = PageData(
        list=[ShipmentOut.model_validate(item) for item in items],
        pageNo=page_no,
        pageSize=page_size,
        total=total,
    )
    return APIResponse(data=page, traceId=new_trace_id())
