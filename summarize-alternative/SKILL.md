---
name: summarize-alternative
description: 使用 playwright-scraper + LLM 实现内容摘要（无需安装外部依赖）
version: 1.0.0
---

# Summarize Alternative

使用已安装的 `playwright-scraper` 技能抓取网页内容，然后用 LLM 进行摘要。

## 前提条件

- 已安装 `playwright-scraper` 技能
- 有可用的 LLM（当前会话已配置）

## 使用方法

### 1. 抓取网页内容

```bash
# 普通网站
node ../playwright-scraper/scripts/playwright-simple.js "https://example.com"

# 有反爬保护的网站
node ../playwright-scraper/scripts/playwright-stealth.js "https://m.discuss.com.hk/#hot"
```

### 2. 让 AI 摘要

将抓取的内容发送给 AI，要求摘要：

```
请摘要以下内容：
[粘贴抓取的内容]

要求：
- 3-5 个要点
- 简洁明了
- 保留关键信息
```

### 3. 一键脚本（可选）

```bash
# 抓取并摘要
./scripts/summarize-url.sh "https://example.com" "short"
```

## 支持的内容类型

| 类型 | 方法 |
|------|------|
| 网页 URL | playwright-scraper |
| PDF 文件 | 上传文件 + LLM 摘要 |
| YouTube | 使用 tavily 搜索转录或使用 deep-scraper |
| 本地文本 | 直接发送给 LLM |

## 优势

- ✅ 无需额外安装
- ✅ 使用现有技能组合
- ✅ 可自定义摘要长度和风格
- ✅ 支持中文输出

---

_基于已有技能组合，无需 brew 安装_
