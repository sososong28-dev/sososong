# NotebookLM Skill - 快速上手指南

## ✅ 安装状态

| 组件 | 状态 |
|------|------|
| Python 虚拟环境 | ✅ 已安装 |
| 依赖包 (patchright, dotenv) | ✅ 已安装 |
| Chrome 浏览器 | ✅ 已安装 |
| 认证状态 | ⏳ 待认证 |

---

## 🚀 首次使用 - 认证步骤

### 1. 运行认证命令

```bash
cd /Users/sososong/.openclaw/workspace/skills/notebooklm/notebooklm-skill-master

# 运行认证（会打开浏览器窗口）
source .venv/bin/activate
python scripts/run.py auth_manager.py setup
```

### 2. 手动登录 Google

- 浏览器窗口会自动打开
- 登录你的 Google 账号
- 访问 NotebookLM: https://notebooklm.google.com
- 确保能看到你的 notebooks

---

## 📚 核心功能

### 1️⃣ 查看 notebooks

```bash
python scripts/run.py notebook_manager.py list
```

### 2️⃣ 添加 notebook 到库

```bash
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/你的 notebook ID" \
  --name "笔记名称" \
  --description "笔记内容描述" \
  --topics "主题 1,主题 2,主题 3"
```

### 3️⃣ 提问（基于文档内容）

```bash
python scripts/run.py ask_question.py \
  --question "你的问题" \
  --notebook-id "notebook ID"
```

---

## 💡 使用场景

| 场景 | 命令 |
|------|------|
| 查询文档内容 | `ask_question.py --question "..."` |
| 管理 notebook 库 | `notebook_manager.py list/add/search` |
| 检查认证状态 | `auth_manager.py status` |

---

## ⚠️ 重要提示

1. **必须使用本地 Claude Code** - Web UI 不支持（沙盒无网络）
2. **浏览器必须可见** - 认证时需要手动登录
3. **每个问题独立** - 无会话持久化
4. **免费账号限制** - 50 次查询/天

---

## 📁 安装位置

```
/Users/sososong/.openclaw/workspace/skills/notebooklm/notebooklm-skill-master/
├── scripts/           # 所有脚本
├── .venv/            # Python 虚拟环境
├── data/             # 认证和库数据
└── requirements.txt  # 依赖
```

---

## 🔧 常用命令

```bash
# 进入目录
cd /Users/sososong/.openclaw/workspace/skills/notebooklm/notebooklm-skill-master

# 激活虚拟环境
source .venv/bin/activate

# 检查认证
python scripts/run.py auth_manager.py status

# 认证（首次使用）
python scripts/run.py auth_manager.py setup

# 列出 notebooks
python scripts/run.py notebook_manager.py list

# 提问
python scripts/run.py ask_question.py --question "问题内容"
```

---

_安装完成时间：2026-03-05 21:00_
