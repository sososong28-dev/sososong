# 旺店通 FastAPI 集成骨架

这是一个面向旺店通开放平台的 FastAPI 集成骨架，包含：

- 基础档案、货品、订单、库存、发货、售后查询接口
- SSE / WebSocket 实时推送接口
- SQLAlchemy 数据模型
- 旺店通 API Client 骨架
- 同步任务与运维接口骨架

## 快速启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r wdt_fastapi/requirements.txt
uvicorn wdt_fastapi.app.main:app --reload
```

默认使用 SQLite：

```env
DATABASE_URL=sqlite:///./wdt_fastapi.db
```

访问：

- OpenAPI: `http://127.0.0.1:8000/docs`
- SSE: `http://127.0.0.1:8000/api/realtime/events`
- WebSocket: `ws://127.0.0.1:8000/ws/realtime`

## 环境变量

复制 `.env.example` 后按需调整：

```bash
cp wdt_fastapi/.env.example wdt_fastapi/.env
```

## 说明

当前版本是“可运行骨架”，重点是把接口边界、数据库结构和实时推送通路先搭起来。
真正对接旺店通前，需要补齐：

- 网关 URL
- 公共参数
- 签名算法
- 错误码处理
- 分页参数
- 回写字段定义
