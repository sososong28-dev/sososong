---
name: apple-reminders-alternative
description: 使用 AppleScript 控制 macOS 提醒事项 App（无需安装外部依赖）
version: 1.0.0
---

# Apple Reminders Alternative (AppleScript)

使用 macOS 原生 AppleScript 控制提醒事项 App，无需安装任何外部工具。

## 前提条件

- macOS 系统
- 允许终端访问提醒事项（系统设置 → 隐私与安全 → 提醒事项）

## 使用方法

```bash
# 列出今日提醒
./scripts/list-reminders.sh

# 添加提醒
./scripts/add-reminder.sh "买牛奶" "个人" "2026-03-06"

# 完成提醒
./scripts/complete-reminder.sh "买牛奶"
```

## 权限设置

首次运行时，系统会提示授权终端访问提醒事项：
1. 打开「系统设置」
2. 隐私与安全 → 提醒事项
3. 勾选「终端」或「zsh」

---

_基于 macOS 原生 AppleScript，无需 brew 安装_
