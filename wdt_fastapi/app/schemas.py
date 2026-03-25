from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    code: str = "0"
    message: str = "ok"
    data: T
    trace_id: str = Field(alias="traceId")

    model_config = ConfigDict(populate_by_name=True)


class PageData(BaseModel, Generic[T]):
    list: list[T]
    page_no: int = Field(alias="pageNo")
    page_size: int = Field(alias="pageSize")
    total: int

    model_config = ConfigDict(populate_by_name=True)


class ShopOut(BaseModel):
    shop_no: str = Field(alias="shopNo")
    shop_name: str = Field(alias="shopName")
    platform_code: str | None = Field(default=None, alias="platformCode")
    status: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class WarehouseOut(BaseModel):
    warehouse_no: str = Field(alias="warehouseNo")
    warehouse_name: str = Field(alias="warehouseName")
    warehouse_type: str | None = Field(default=None, alias="warehouseType")
    status: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LogisticsOut(BaseModel):
    logistics_no: str = Field(alias="logisticsNo")
    logistics_name: str = Field(alias="logisticsName")
    status: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class GoodsOut(BaseModel):
    goods_no: str = Field(alias="goodsNo")
    goods_name: str = Field(alias="goodsName")
    brand_no: str | None = Field(default=None, alias="brandNo")
    class_no: str | None = Field(default=None, alias="classNo")
    status: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class GoodsSpecOut(BaseModel):
    spec_no: str = Field(alias="specNo")
    goods_no: str = Field(alias="goodsNo")
    spec_name: str = Field(alias="specName")
    barcode: str | None = None
    status: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OrderItemOut(BaseModel):
    line_no: str | None = Field(default=None, alias="lineNo")
    spec_no: str | None = Field(default=None, alias="specNo")
    goods_name: str | None = Field(default=None, alias="goodsName")
    spec_name: str | None = Field(default=None, alias="specName")
    qty: Decimal
    price: Decimal | None = None
    amount: Decimal | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OrderOut(BaseModel):
    order_no: str = Field(alias="orderNo")
    src_order_no: str | None = Field(default=None, alias="srcOrderNo")
    shop_no: str | None = Field(default=None, alias="shopNo")
    warehouse_no: str | None = Field(default=None, alias="warehouseNo")
    buyer_nick: str | None = Field(default=None, alias="buyerNick")
    order_status: str | None = Field(default=None, alias="orderStatus")
    pay_status: str | None = Field(default=None, alias="payStatus")
    logistics_name: str | None = Field(default=None, alias="logisticsName")
    logistics_bill_no: str | None = Field(default=None, alias="logisticsBillNo")
    paid_amount: Decimal | None = Field(default=None, alias="paidAmount")
    order_time: datetime | None = Field(default=None, alias="orderTime")
    consign_time: datetime | None = Field(default=None, alias="consignTime")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class OrderDetailOut(BaseModel):
    base: OrderOut
    items: list[OrderItemOut]


class StockSnapshotOut(BaseModel):
    warehouse_no: str = Field(alias="warehouseNo")
    spec_no: str = Field(alias="specNo")
    stock_num: Decimal = Field(alias="stockNum")
    available_num: Decimal = Field(alias="availableNum")
    order_num: Decimal = Field(alias="orderNum")
    sending_num: Decimal = Field(alias="sendingNum")
    locked_num: Decimal = Field(alias="lockedNum")
    snapshot_time: datetime | None = Field(default=None, alias="snapshotTime")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class StockChangeOut(BaseModel):
    change_key: str = Field(alias="changeKey")
    warehouse_no: str = Field(alias="warehouseNo")
    spec_no: str = Field(alias="specNo")
    change_type: str | None = Field(default=None, alias="changeType")
    biz_no: str | None = Field(default=None, alias="bizNo")
    before_num: Decimal | None = Field(default=None, alias="beforeNum")
    change_num: Decimal | None = Field(default=None, alias="changeNum")
    after_num: Decimal | None = Field(default=None, alias="afterNum")
    change_time: datetime | None = Field(default=None, alias="changeTime")
    ack_status: int = Field(alias="ackStatus")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ShipmentOut(BaseModel):
    sync_key: str = Field(alias="syncKey")
    order_no: str | None = Field(default=None, alias="orderNo")
    stockout_no: str | None = Field(default=None, alias="stockoutNo")
    logistics_no: str | None = Field(default=None, alias="logisticsNo")
    logistics_bill_no: str | None = Field(default=None, alias="logisticsBillNo")
    shipment_status: str | None = Field(default=None, alias="shipmentStatus")
    sync_time: datetime | None = Field(default=None, alias="syncTime")
    ack_status: int = Field(alias="ackStatus")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RefundOut(BaseModel):
    refund_no: str = Field(alias="refundNo")
    order_no: str | None = Field(default=None, alias="orderNo")
    shop_no: str | None = Field(default=None, alias="shopNo")
    refund_type: str | None = Field(default=None, alias="refundType")
    refund_status: str | None = Field(default=None, alias="refundStatus")
    refund_amount: Decimal | None = Field(default=None, alias="refundAmount")
    apply_time: datetime | None = Field(default=None, alias="applyTime")
    finish_time: datetime | None = Field(default=None, alias="finishTime")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SyncTaskOut(BaseModel):
    task_code: str = Field(alias="taskCode")
    task_name: str = Field(alias="taskName")
    enabled: int
    interval_seconds: int | None = Field(default=None, alias="intervalSeconds")
    last_status: str | None = Field(default=None, alias="lastStatus")
    last_message: str | None = Field(default=None, alias="lastMessage")
    last_run_time: datetime | None = Field(default=None, alias="lastRunTime")
    last_success_time: datetime | None = Field(default=None, alias="lastSuccessTime")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DashboardOverview(BaseModel):
    today_orders: int = Field(alias="todayOrders")
    today_paid_orders: int = Field(alias="todayPaidOrders")
    today_shipped_orders: int = Field(alias="todayShippedOrders")
    today_refunds: int = Field(alias="todayRefunds")
    low_stock_sku_count: int = Field(alias="lowStockSkuCount")
    sync_fail_count: int = Field(alias="syncFailCount")

    model_config = ConfigDict(populate_by_name=True)


class TriggerSyncRequest(BaseModel):
    event_type: str = Field(alias="eventType")
    payload: dict = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)
