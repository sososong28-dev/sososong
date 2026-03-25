from datetime import date, datetime, time

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Order, Refund, ShipmentSyncRecord, StockSnapshot, SyncTask
from ..schemas import APIResponse, DashboardOverview
from ..utils import new_trace_id

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=APIResponse[DashboardOverview])
def get_overview(db: Session = Depends(get_db)) -> APIResponse[DashboardOverview]:
    today_start = datetime.combine(date.today(), time.min)
    today_orders = len(db.scalars(select(Order).where(Order.order_time >= today_start)).all())
    today_paid_orders = len(db.scalars(select(Order).where(Order.pay_status == "paid", Order.order_time >= today_start)).all())
    today_shipped_orders = len(db.scalars(select(ShipmentSyncRecord).where(ShipmentSyncRecord.created_at >= today_start)).all())
    today_refunds = len(db.scalars(select(Refund).where(Refund.created_at >= today_start)).all())
    low_stock_sku_count = db.scalar(select(func.count()).select_from(StockSnapshot).where(StockSnapshot.available_num <= 10)) or 0
    sync_fail_count = db.scalar(select(func.count()).select_from(SyncTask).where(SyncTask.last_status == "failed")) or 0
    data = DashboardOverview(
        todayOrders=today_orders,
        todayPaidOrders=today_paid_orders,
        todayShippedOrders=today_shipped_orders,
        todayRefunds=today_refunds,
        lowStockSkuCount=low_stock_sku_count,
        syncFailCount=sync_fail_count,
    )
    return APIResponse(data=data, traceId=new_trace_id())
