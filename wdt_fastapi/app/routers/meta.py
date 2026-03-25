from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LogisticsCompany, Shop, Warehouse
from ..schemas import APIResponse, LogisticsOut, ShopOut, WarehouseOut
from ..utils import new_trace_id

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/shops", response_model=APIResponse[dict])
def list_shops(
    keyword: str | None = Query(default=None),
    status: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    stmt = select(Shop).order_by(Shop.id.desc())
    if keyword:
        stmt = stmt.where(Shop.shop_name.contains(keyword))
    if status is not None:
        stmt = stmt.where(Shop.status == status)
    items = db.scalars(stmt).all()
    return APIResponse(data={"list": [ShopOut.model_validate(item).model_dump(by_alias=True) for item in items]}, traceId=new_trace_id())


@router.get("/warehouses", response_model=APIResponse[dict])
def list_warehouses(db: Session = Depends(get_db)) -> APIResponse[dict]:
    items = db.scalars(select(Warehouse).order_by(Warehouse.id.desc())).all()
    return APIResponse(data={"list": [WarehouseOut.model_validate(item).model_dump(by_alias=True) for item in items]}, traceId=new_trace_id())


@router.get("/logistics", response_model=APIResponse[dict])
def list_logistics(db: Session = Depends(get_db)) -> APIResponse[dict]:
    items = db.scalars(select(LogisticsCompany).order_by(LogisticsCompany.id.desc())).all()
    return APIResponse(data={"list": [LogisticsOut.model_validate(item).model_dump(by_alias=True) for item in items]}, traceId=new_trace_id())
