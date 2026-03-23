from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Refund
from ..schemas import APIResponse, PageData, RefundOut
from ..utils import new_trace_id

router = APIRouter(prefix="/api/refunds", tags=["refunds"])


@router.get("", response_model=APIResponse[PageData[RefundOut]])
def list_refunds(
    shop_no: str | None = Query(default=None, alias="shopNo"),
    refund_status: str | None = Query(default=None, alias="refundStatus"),
    page_no: int = Query(default=1, alias="pageNo", ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=100),
    db: Session = Depends(get_db),
) -> APIResponse[PageData[RefundOut]]:
    stmt = select(Refund).order_by(Refund.id.desc())
    if shop_no:
        stmt = stmt.where(Refund.shop_no == shop_no)
    if refund_status:
        stmt = stmt.where(Refund.refund_status == refund_status)
    items = db.scalars(stmt.offset((page_no - 1) * page_size).limit(page_size)).all()
    total = len(db.scalars(select(Refund)).all())
    page = PageData(
        list=[RefundOut.model_validate(item) for item in items],
        pageNo=page_no,
        pageSize=page_size,
        total=total,
    )
    return APIResponse(data=page, traceId=new_trace_id())
