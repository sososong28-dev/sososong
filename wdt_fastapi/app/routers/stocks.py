from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import StockChangeRecord, StockSnapshot
from ..schemas import APIResponse, PageData, StockChangeOut, StockSnapshotOut
from ..utils import new_trace_id

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("", response_model=APIResponse[PageData[StockSnapshotOut]])
def list_stocks(
    warehouse_no: str | None = Query(default=None, alias="warehouseNo"),
    spec_no: str | None = Query(default=None, alias="specNo"),
    low_stock_only: bool = Query(default=False, alias="lowStockOnly"),
    threshold: Decimal = Query(default=10, ge=0),
    page_no: int = Query(default=1, alias="pageNo", ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=100),
    db: Session = Depends(get_db),
) -> APIResponse[PageData[StockSnapshotOut]]:
    stmt = select(StockSnapshot).order_by(StockSnapshot.id.desc())
    if warehouse_no:
        stmt = stmt.where(StockSnapshot.warehouse_no == warehouse_no)
    if spec_no:
        stmt = stmt.where(StockSnapshot.spec_no == spec_no)
    if low_stock_only:
        stmt = stmt.where(StockSnapshot.available_num <= threshold)
    items = db.scalars(stmt.offset((page_no - 1) * page_size).limit(page_size)).all()
    total = len(db.scalars(select(StockSnapshot)).all())
    page = PageData(
        list=[StockSnapshotOut.model_validate(item) for item in items],
        pageNo=page_no,
        pageSize=page_size,
        total=total,
    )
    return APIResponse(data=page, traceId=new_trace_id())


@router.get("/changes", response_model=APIResponse[PageData[StockChangeOut]])
def list_stock_changes(
    warehouse_no: str | None = Query(default=None, alias="warehouseNo"),
    spec_no: str | None = Query(default=None, alias="specNo"),
    page_no: int = Query(default=1, alias="pageNo", ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=100),
    db: Session = Depends(get_db),
) -> APIResponse[PageData[StockChangeOut]]:
    stmt = select(StockChangeRecord).order_by(StockChangeRecord.id.desc())
    if warehouse_no:
        stmt = stmt.where(StockChangeRecord.warehouse_no == warehouse_no)
    if spec_no:
        stmt = stmt.where(StockChangeRecord.spec_no == spec_no)
    items = db.scalars(stmt.offset((page_no - 1) * page_size).limit(page_size)).all()
    total = len(db.scalars(select(StockChangeRecord)).all())
    page = PageData(
        list=[StockChangeOut.model_validate(item) for item in items],
        pageNo=page_no,
        pageSize=page_size,
        total=total,
    )
    return APIResponse(data=page, traceId=new_trace_id())
