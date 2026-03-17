# sososong

一个可在本地运行的 **AI 网页端整合原型**（OpenClaw / Codex / GPT），用于实现：
- 站点配置统一管理
- Prompt 注入脚本生成
- 对话历史归档

> 当前仓库实现的是可运行核心层（Swift Package + CLI），便于后续接入 iOS `WKWebView` UI。

## 已完成内容

### 1) Provider 目录加载
- 从 `providers.json` 读取 OpenClaw/Codex/GPT 配置。
- 字段包含：主页 URL、输入框选择器、提交按钮选择器。

### 2) Prompt 注入脚本生成
- 自动转义换行、引号与反斜杠。
- 输出可直接用于 `WKWebView.evaluateJavaScript(...)` 的 JS 片段。

### 3) 对话归档存储
- JSON 文件持久化。
- 支持追加与全量读取，便于后续做“历史记录”页面。

### 4) CLI 试运行入口
- 命令：`swift run sososong-cli`
- 启动时会：
  1. 加载 Provider 列表
  2. 预览注入脚本
  3. 写入并读取一条示例归档

## 目录结构

```text
.
├── Package.swift
├── Sources
│   ├── SosoSongCLI
│   │   └── main.swift
│   └── SosoSongCore
│       ├── ConversationArchiveStore.swift
│       ├── Models.swift
│       ├── PromptInjectionBuilder.swift
│       ├── ProviderCatalog.swift
│       └── Resources
│           └── providers.json
└── Tests
    └── SosoSongCoreTests
        └── SosoSongCoreTests.swift
```

## 本地运行

```bash
swift test
swift run sososong-cli
```

## 下一步（iOS 接入）
1. 新建 iOS App target（SwiftUI）。
2. 用 `UIViewRepresentable` 封装 `WKWebView`。
3. 将 `SosoSongCore` 作为业务层依赖：
   - 读取 provider 配置
   - 生成注入脚本
   - 存储会话历史
4. 实现账号隔离（不同 `WKWebsiteDataStore`）。

## 合规说明
- 本项目聚焦多平台整合效率工具。
- 不提供绕过检测、破解风控等能力。
