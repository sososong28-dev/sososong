# Windows 定时执行方案

适用于 OpenClaw 在 Windows 环境中按固定时间生成“避孕套行业竞品情报日报”。

## 推荐执行架构

建议拆成三层：

1. **采集层**：搜索、抓网页、抓电商页面、抓评论样本、保存原始 JSON/CSV/HTML。
2. **分析层**：去重、归类、提炼、生成结构化 Markdown。
3. **生成发送层**：Markdown 转 PDF，保存文件，并推送摘要与附件。

这种分层方式能降低单点失败导致整条链路中断的风险。

## 推荐目录约定

```text
C:\OpenClaw\skills\competitor-intel-daily-cn\
C:\OpenClaw\data\competitor-intel\raw\
C:\OpenClaw\data\competitor-intel\cleaned\
C:\OpenClaw\data\competitor-intel\reports\
```

## 推荐调度时间

- **早晨版**：每天 08:30，汇总前一天 08:30 到当天 08:30 的数据。
- **晚间版**：每天 18:30，适合当天复盘。
- 如果团队需要预警，可额外加每 2-4 小时的轻量扫描任务。

## 执行入口建议

用一个统一入口，例如：

```powershell
openclaw run --skill competitor-intel-daily-cn --input "生成今日避孕套行业竞品情报日报，并输出 PDF 与消息摘要。"
```

如果你的 OpenClaw 分发方式不同，也可以改成：

```powershell
python collect.py
python analyze.py
python render_pdf.py
python send_digest.py
```

## 在任务计划程序中创建任务

### 方法一：图形界面

1. 打开“任务计划程序”。
2. 选择“创建任务”。
3. 名称填写：`Competitor Intel Daily CN`。
4. 触发器选择“每天”，设置固定执行时间。
5. 操作选择“启动程序”。
6. 程序填写：`powershell.exe`
7. 参数填写：

```powershell
-ExecutionPolicy Bypass -File "C:\OpenClaw\skills\competitor-intel-daily-cn\scripts\register_daily_task.ps1" -RunNow
```

如果你只想运行主流程，把参数替换成实际日报命令。

### 方法二：命令行

```powershell
schtasks /Create /SC DAILY /TN "Competitor Intel Daily CN" /TR "powershell.exe -ExecutionPolicy Bypass -File C:\OpenClaw\skills\competitor-intel-daily-cn\scripts\run_daily_report.ps1" /ST 08:30
```

## 失败重试建议

- 首次失败后 15 分钟重试一次。
- 同一任务最多重试 3 次。
- 抓取失败原因写入日志，并在日报附录中标记。

## 日志建议

建议每次任务产出：

- `run.log`：主流程日志
- `failed_sources.json`：抓取失败源与错误原因
- `report_manifest.json`：报告文件、摘要文件、发送状态

## 发送建议

至少准备两类输出：

1. **PDF 正文**：发管理层或归档。
2. **消息摘要**：发 Telegram / 邮件 / 企业微信 / 钉钉。

若触发预警事件，建议立即单独推送，而不是等日报。
