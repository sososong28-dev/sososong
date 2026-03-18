---
name: apple-notes-alternative
description: 使用 AppleScript 控制 macOS 备忘录 App（无需安装外部依赖）
version: 1.0.0
---

# Apple Notes Alternative (AppleScript)

使用 macOS 原生 AppleScript 控制备忘录 App，无需安装任何外部工具。

## 前提条件

- macOS 系统
- 允许终端访问备忘录（系统设置 → 隐私与安全 → 备忘录）

## 使用方法

```bash
# 列出所有备忘录
./scripts/list-notes.sh

# 创建新备忘录
./scripts/create-note.sh "标题" "内容"

# 搜索备忘录
./scripts/search-notes.sh "关键词"
```

## 权限设置

首次运行时，系统会提示授权终端访问备忘录：
1. 打开「系统设置」
2. 隐私与安全 → 备忘录
3. 勾选「终端」或「zsh」

---

_基于 macOS 原生 AppleScript，无需 brew 安装_
