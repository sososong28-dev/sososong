# OpenClaw 多节点统一监控与调度控制台（MVP）

基于 **FastAPI + SQLite + Paramiko + 原生 HTML/JS** 的本地运维控制中心。

## 新增能力
- 新增 **Win1 / Win2 持续监控**：应用启动后会按 `PROBE_INTERVAL_SECONDS` 周期自动巡检所有节点。
- 新增 **全量巡检按钮**：Dashboard 可立即触发包含 `win-openclaw-01` 与 `win-openclaw-02` 在内的全节点检查。
- 新增 **AI Token 用量记录**：从本地/远程日志中解析 `prompt_tokens / completion_tokens / total_tokens` 并入库。
- 新增 **Token 用量展示**：Dashboard 显示累计 token，节点详情与任务页显示最近 token 记录。
- 新增 **Driftwatch 风格控制台界面**：采用左侧导航、中间仪表盘、右侧运行摘要的玻璃拟态布局。

## 功能
- Dashboard 展示 3 个节点状态、OpenClaw 状态、最近心跳、错误摘要、最近 token 用量
- 节点详情：机器指标、进程状态、日志摘要、最近任务、最近 token 用量
- 任务页：最近任务执行记录 + 最近 AI Token 用量
- API：
  - `GET /api/health`
  - `GET /api/nodes`
  - `GET /api/nodes/:id`
  - `GET /api/tasks`
  - `GET /api/token-usage`
  - `POST /api/nodes/check-all`
  - `POST /api/nodes/:id/check`
  - `POST /api/nodes/:id/action`（白名单动作）
- 真实探测：
  - Mac 本机使用 `psutil` + 本地进程检查 + 本地日志 tail
  - Windows 节点使用 SSH + PowerShell 采集 CPU/内存/磁盘/进程/日志 tail

## 安全增强
- API Token 鉴权：除 `/api/health` 外 API 需携带 `X-API-Token`
- Action 参数白名单与 Pydantic 强校验
- `node_id` 路径参数正则校验，禁止非法格式
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
   - `ENABLE_BACKGROUND_MONITOR=true`：启用后台持续巡检
   - `PROBE_INTERVAL_SECONDS=60`：巡检频率
3. 编辑 `config/nodes.yaml`：设置 Win1 / Win2 的 SSH 主机、用户、进程名、日志路径。

## 日志中的 Token 用量格式
系统会从日志中解析类似格式：
```text
provider=openai model=gpt-4.1 prompt_tokens=120 completion_tokens=30 total_tokens=150
provider=anthropic model=claude-3.7 input_tokens=200 output_tokens=50 total_tokens=250
```

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
curl -X POST -H "X-API-Token: change-me" http://127.0.0.1:8000/api/nodes/check-all
curl -H "X-API-Token: change-me" http://127.0.0.1:8000/api/token-usage
```

## 已知限制
- Windows SSH 登录默认依赖已有密钥/认证配置（未强制实现密码登录）
- Token 用量依赖日志中存在标准 token 字段
- 若 Win 节点日志路径不可访问，则仍可完成系统资源巡检，但 token 用量会缺失
