# OpenClaw 多节点统一监控与调度控制台（MVP）

基于 **FastAPI + SQLite + Paramiko + 原生 HTML/JS** 的本地运维控制中心。

## 功能
- Dashboard 展示 3 个节点状态、OpenClaw 状态、最近心跳、错误摘要
- 节点详情：机器指标、进程状态、日志摘要、最近任务
- 任务页：最近任务执行记录
- API：
  - `GET /api/health`
  - `GET /api/nodes`
  - `GET /api/nodes/:id`
  - `GET /api/tasks`
  - `POST /api/nodes/:id/check`
  - `POST /api/nodes/:id/action`（白名单动作）
- 真实探测：
  - Mac 本机使用 `psutil` + 本地进程检查
  - Windows 节点使用 SSH + PowerShell 采集信息

## 安全增强（本次修复）
- API Token 鉴权：除 `/api/health` 外 API 需携带 `X-API-Token`
- Action 参数白名单与 Pydantic 强校验
- `node_id` 路径参数正则校验，禁止非法格式
- 全局节点配置状态移除，改为按配置文件读取
- 统一日志记录 + 未处理异常兜底返回

## 项目结构

```bash
app/
  main.py
  config.py
  database.py
  models.py
  probe.py
  schemas.py
  templates/
  static/
config/
  nodes.yaml
  nodes.example.yaml
scripts/
  init_db.py
  start.sh
tests/
  test_api.py
  test_probe.py
  test_db.py
e2e/
  dashboard.spec.js
```

## 配置
1. 复制环境变量：
```bash
cp .env.example .env
```
2. 编辑 `.env`：
   - `API_TOKEN`：API 访问令牌
   - `NODES_CONFIG_PATH`：建议绝对路径
3. 编辑 `config/nodes.yaml`：设置 Win 节点 SSH 主机、用户、进程名、日志路径。

## 启动
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

也可以使用：
```bash
bash scripts/start.sh
```

访问地址：`http://127.0.0.1:8000`

## 测试
### 后端
```bash
pytest -q
```

### 前端 E2E（Playwright）
```bash
npm install
npx playwright install chromium
npm run test:e2e
```

## API 鉴权示例
```bash
curl -H "X-API-Token: change-me" http://127.0.0.1:8000/api/nodes
```

## 已知限制
- Windows SSH 登录默认依赖已有密钥/认证配置（未强制实现密码登录）
- OpenClaw 进程名需与你本机实际进程名一致
- 日志路径需可访问，无法访问时会记录 `log unavailable`
