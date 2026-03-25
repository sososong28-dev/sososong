from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Shop(TimestampMixin, Base):
    __tablename__ = "shops"

    id: Mapped[int] = mapped_column(primary_key=True)
    shop_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    shop_name: Mapped[str] = mapped_column(String(128), index=True)
    platform_code: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[int] = mapped_column(default=1)
    raw_json: Mapped[dict | None] = mapped_column(JSON)


class Warehouse(TimestampMixin, Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    warehouse_name: Mapped[str] = mapped_column(String(128), index=True)
    warehouse_type: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[int] = mapped_column(default=1)
    raw_json: Mapped[dict | None] = mapped_column(JSON)


class LogisticsCompany(TimestampMixin, Base):
    __tablename__ = "logistics_companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    logistics_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    logistics_name: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[int] = mapped_column(default=1)
    raw_json: Mapped[dict | None] = mapped_column(JSON)


class Goods(TimestampMixin, Base):
    __tablename__ = "goods"

    id: Mapped[int] = mapped_column(primary_key=True)
    goods_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    goods_name: Mapped[str] = mapped_column(String(255), index=True)
    brand_no: Mapped[str | None] = mapped_column(String(64), index=True)
    class_no: Mapped[str | None] = mapped_column(String(64), index=True)
    status: Mapped[int] = mapped_column(default=1)
    raw_json: Mapped[dict | None] = mapped_column(JSON)


class GoodsSpec(TimestampMixin, Base):
    __tablename__ = "goods_specs"

    id: Mapped[int] = mapped_column(primary_key=True)
    spec_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    goods_no: Mapped[str] = mapped_column(String(64), index=True)
    spec_name: Mapped[str] = mapped_column(String(255), index=True)
    barcode: Mapped[str | None] = mapped_column(String(128), index=True)
    status: Mapped[int] = mapped_column(default=1)
    raw_json: Mapped[dict | None] = mapped_column(JSON)


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    src_order_no: Mapped[str | None] = mapped_column(String(64), index=True)
    shop_no: Mapped[str | None] = mapped_column(String(64), index=True)
    warehouse_no: Mapped[str | None] = mapped_column(String(64), index=True)
    buyer_nick: Mapped[str | None] = mapped_column(String(128))
    order_status: Mapped[str | None] = mapped_column(String(64), index=True)
    pay_status: Mapped[str | None] = mapped_column(String(64), index=True)
    logistics_name: Mapped[str | None] = mapped_column(String(128))
    logistics_bill_no: Mapped[str | None] = mapped_column(String(128))
    paid_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    order_time: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    consign_time: Mapped[datetime | None] = mapped_column(DateTime)
    modified: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    raw_json: Mapped[dict | None] = mapped_column(JSON)


class OrderItem(TimestampMixin, Base):
    __tablename__ = "order_items"
    __table_args__ = (UniqueConstraint("order_no", "line_no", name="uk_order_line"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(64), index=True)
    line_no: Mapped[str | None] = mapped_column(String(64))
    spec_no: Mapped[str | None] = mapped_column(String(64), index=True)
    goods_name: Mapped[str | None] = mapped_column(String(255))
    spec_name: Mapped[str | None] = mapped_column(String(255))
    qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=0)
    price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    raw_json: Mapped[dict | None] = mapped_column(JSON)


class StockSnapshot(TimestampMixin, Base):
    __tablename__ = "stock_snapshots"
    __table_args__ = (UniqueConstraint("warehouse_no", "spec_no", name="uk_warehouse_spec"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_no: Mapped[str] = mapped_column(String(64), index=True)
    spec_no: Mapped[str] = mapped_column(String(64), index=True)
    stock_num: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=0)
    available_num: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=0)
    order_num: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=0)
    sending_num: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=0)
    locked_num: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=0)
    snapshot_time: Mapped[datetime | None] = mapped_column(DateTime, index=True)


class StockChangeRecord(TimestampMixin, Base):
    __tablename__ = "stock_change_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    change_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    warehouse_no: Mapped[str] = mapped_column(String(64), index=True)
    spec_no: Mapped[str] = mapped_column(String(64), index=True)
    change_type: Mapped[str | None] = mapped_column(String(64))
    biz_no: Mapped[str | None] = mapped_column(String(64))
    before_num: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    change_num: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    after_num: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    change_time: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    ack_status: Mapped[int] = mapped_column(default=0, index=True)
    ack_message: Mapped[str | None] = mapped_column(String(255))
    raw_json: Mapped[dict | None] = mapped_column(JSON)


class ShipmentSyncRecord(TimestampMixin, Base):
    __tablename__ = "shipment_sync_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    sync_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    order_no: Mapped[str | None] = mapped_column(String(64), index=True)
    stockout_no: Mapped[str | None] = mapped_column(String(64), index=True)
    logistics_no: Mapped[str | None] = mapped_column(String(64))
    logistics_bill_no: Mapped[str | None] = mapped_column(String(128))
    shipment_status: Mapped[str | None] = mapped_column(String(64))
    sync_time: Mapped[datetime | None] = mapped_column(DateTime)
    ack_status: Mapped[int] = mapped_column(default=0, index=True)
    ack_message: Mapped[str | None] = mapped_column(String(255))
    raw_json: Mapped[dict | None] = mapped_column(JSON)


class Refund(TimestampMixin, Base):
    __tablename__ = "refunds"

    id: Mapped[int] = mapped_column(primary_key=True)
    refund_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    order_no: Mapped[str | None] = mapped_column(String(64), index=True)
    shop_no: Mapped[str | None] = mapped_column(String(64), index=True)
    refund_type: Mapped[str | None] = mapped_column(String(64))
    refund_status: Mapped[str | None] = mapped_column(String(64), index=True)
    refund_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    apply_time: Mapped[datetime | None] = mapped_column(DateTime)
    finish_time: Mapped[datetime | None] = mapped_column(DateTime)
    modified: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    raw_json: Mapped[dict | None] = mapped_column(JSON)


class SyncTask(TimestampMixin, Base):
    __tablename__ = "sync_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    task_name: Mapped[str] = mapped_column(String(128))
    enabled: Mapped[int] = mapped_column(default=1)
    interval_seconds: Mapped[int | None]
    last_status: Mapped[str | None] = mapped_column(String(32))
    last_message: Mapped[str | None] = mapped_column(String(255))
    last_run_time: Mapped[datetime | None] = mapped_column(DateTime)
    last_success_time: Mapped[datetime | None] = mapped_column(DateTime)


class SyncCursor(Base):
    __tablename__ = "sync_cursors"
    __table_args__ = (UniqueConstraint("task_code", "cursor_type", name="uk_task_cursor"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    task_code: Mapped[str] = mapped_column(String(64), index=True)
    cursor_type: Mapped[str] = mapped_column(String(64))
    cursor_value: Mapped[str | None] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class ApiRequestLog(Base):
    __tablename__ = "api_request_logs"
    __table_args__ = (Index("idx_service_name_created_at", "service_name", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    service_name: Mapped[str] = mapped_column(String(128))
    request_body: Mapped[str | None] = mapped_column(Text)
    response_body: Mapped[str | None] = mapped_column(Text)
    success: Mapped[int] = mapped_column(default=0, index=True)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_message: Mapped[str | None] = mapped_column(String(255))
    duration_ms: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
