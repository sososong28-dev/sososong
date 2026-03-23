from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Goods, GoodsSpec
from ..schemas import APIResponse, GoodsOut, GoodsSpecOut, PageData
from ..utils import new_trace_id

router = APIRouter(prefix="/api/goods", tags=["goods"])


@router.get("", response_model=APIResponse[PageData[GoodsOut]])
def list_goods(
    keyword: str | None = None,
    page_no: int = Query(default=1, alias="pageNo", ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=100),
    db: Session = Depends(get_db),
) -> APIResponse[PageData[GoodsOut]]:
    stmt = select(Goods).order_by(Goods.id.desc())
    if keyword:
        stmt = stmt.where(Goods.goods_name.contains(keyword))
    items = db.scalars(stmt.offset((page_no - 1) * page_size).limit(page_size)).all()
    total = len(db.scalars(select(Goods)).all())
    page = PageData(
        list=[GoodsOut.model_validate(item) for item in items],
        pageNo=page_no,
        pageSize=page_size,
        total=total,
    )
    return APIResponse(data=page, traceId=new_trace_id())


@router.get("/specs", response_model=APIResponse[PageData[GoodsSpecOut]])
def list_goods_specs(
    keyword: str | None = None,
    page_no: int = Query(default=1, alias="pageNo", ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=100),
    db: Session = Depends(get_db),
) -> APIResponse[PageData[GoodsSpecOut]]:
    stmt = select(GoodsSpec).order_by(GoodsSpec.id.desc())
    if keyword:
        stmt = stmt.where(GoodsSpec.spec_name.contains(keyword))
    items = db.scalars(stmt.offset((page_no - 1) * page_size).limit(page_size)).all()
    total = len(db.scalars(select(GoodsSpec)).all())
    page = PageData(
        list=[GoodsSpecOut.model_validate(item) for item in items],
        pageNo=page_no,
        pageSize=page_size,
        total=total,
    )
    return APIResponse(data=page, traceId=new_trace_id())
