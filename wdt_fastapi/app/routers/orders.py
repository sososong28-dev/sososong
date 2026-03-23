from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Order, OrderItem
from ..schemas import APIResponse, OrderDetailOut, OrderItemOut, OrderOut, PageData
from ..utils import new_trace_id

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=APIResponse[PageData[OrderOut]])
def list_orders(
    keyword: str | None = None,
    shop_no: str | None = Query(default=None, alias="shopNo"),
    order_status: str | None = Query(default=None, alias="orderStatus"),
    page_no: int = Query(default=1, alias="pageNo", ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=100),
    db: Session = Depends(get_db),
) -> APIResponse[PageData[OrderOut]]:
    stmt = select(Order).order_by(Order.id.desc())
    if keyword:
        stmt = stmt.where(Order.order_no.contains(keyword) | Order.src_order_no.contains(keyword))
    if shop_no:
        stmt = stmt.where(Order.shop_no == shop_no)
    if order_status:
        stmt = stmt.where(Order.order_status == order_status)
    items = db.scalars(stmt.offset((page_no - 1) * page_size).limit(page_size)).all()
    total = len(db.scalars(select(Order)).all())
    page = PageData(
        list=[OrderOut.model_validate(item) for item in items],
        pageNo=page_no,
        pageSize=page_size,
        total=total,
    )
    return APIResponse(data=page, traceId=new_trace_id())


@router.get("/{order_no}", response_model=APIResponse[OrderDetailOut])
def get_order_detail(order_no: str, db: Session = Depends(get_db)) -> APIResponse[OrderDetailOut]:
    order = db.scalar(select(Order).where(Order.order_no == order_no))
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    items = db.scalars(select(OrderItem).where(OrderItem.order_no == order_no)).all()
    detail = OrderDetailOut(
        base=OrderOut.model_validate(order),
        items=[OrderItemOut.model_validate(item) for item in items],
    )
    return APIResponse(data=detail, traceId=new_trace_id())
