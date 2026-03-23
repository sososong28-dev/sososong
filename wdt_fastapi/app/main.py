from contextlib import asynccontextmanager
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import FastAPI
from sqlalchemy import select

from .config import get_settings
from .database import Base, SessionLocal, engine
from .models import Goods, GoodsSpec, LogisticsCompany, Order, OrderItem, Shop, StockSnapshot, SyncTask, Warehouse
from .routers import dashboard, goods, meta, orders, realtime, refunds, shipments, stocks, sync


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    yield


app = FastAPI(title=get_settings().app_name, debug=get_settings().app_debug, lifespan=lifespan)
app.include_router(meta.router)
app.include_router(goods.router)
app.include_router(orders.router)
app.include_router(stocks.router)
app.include_router(shipments.router)
app.include_router(refunds.router)
app.include_router(dashboard.router)
app.include_router(sync.router)
app.include_router(realtime.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "旺店通 FastAPI integration scaffold is running"}


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        has_shop = db.scalar(select(Shop.id).limit(1))
        if has_shop:
            return

        db.add_all(
            [
                Shop(shop_no="TMALL01", shop_name="天猫旗舰店", platform_code="tmall", status=1),
                Warehouse(warehouse_no="WH01", warehouse_name="上海仓", warehouse_type="self", status=1),
                LogisticsCompany(logistics_no="YTO", logistics_name="圆通", status=1),
                Goods(goods_no="G001", goods_name="示例商品", brand_no="B001", class_no="C001", status=1),
                GoodsSpec(spec_no="SKU001", goods_no="G001", spec_name="默认规格", barcode="690000000001", status=1),
                Order(
                    order_no="SO202603230001",
                    src_order_no="TB123456789",
                    shop_no="TMALL01",
                    warehouse_no="WH01",
                    buyer_nick="demo-user",
                    order_status="待发货",
                    pay_status="paid",
                    logistics_name="圆通",
                    logistics_bill_no="YT123456789",
                    paid_amount=Decimal("199.00"),
                    order_time=datetime.now(timezone.utc),
                    modified=datetime.now(timezone.utc),
                ),
                OrderItem(
                    order_no="SO202603230001",
                    line_no="1",
                    spec_no="SKU001",
                    goods_name="示例商品",
                    spec_name="默认规格",
                    qty=Decimal("2"),
                    price=Decimal("99.50"),
                    amount=Decimal("199.00"),
                ),
                StockSnapshot(
                    warehouse_no="WH01",
                    spec_no="SKU001",
                    stock_num=Decimal("100"),
                    available_num=Decimal("88"),
                    order_num=Decimal("10"),
                    sending_num=Decimal("2"),
                    locked_num=Decimal("0"),
                    snapshot_time=datetime.now(timezone.utc),
                ),
                SyncTask(task_code="sync_stock_change", task_name="库存变化同步", enabled=1, interval_seconds=10, last_status="idle"),
                SyncTask(task_code="sync_shipment_change", task_name="发货变化同步", enabled=1, interval_seconds=10, last_status="idle"),
                SyncTask(task_code="sync_orders", task_name="订单增量同步", enabled=1, interval_seconds=30, last_status="idle"),
            ]
        )
        db.commit()
    finally:
        db.close()
