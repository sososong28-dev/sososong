# 推送到 GitHub 指南

## 当前状态

✅ 代码已提交到本地仓库
- Commit: `6087fe7`
- 分支：`codex/develop-openclaw-multi-node-monitoring-console`
- 修改：12 个文件，1328 行新增，144 行删除

❌ 推送失败原因：需要 GitHub 认证

---

## 推送方法（任选其一）

### 方法 1：使用 GitHub Desktop（最简单）⭐

1. **下载并安装 GitHub Desktop**
   ```
   https://desktop.github.com/
   ```

2. **登录 GitHub**
   - 打开 GitHub Desktop
   - 使用 GitHub 账号登录

3. **添加本地仓库**
   - File → Add Local Repository
   - 选择路径：`/Users/sososong/.openclaw/workspace/monitoring-console`
   - 点击 "Add Repository"

4. **推送**
   - 点击顶部 "Push origin" 按钮
   - 完成！✅

---

### 方法 2：使用 macOS 钥匙串

1. **打开终端，执行**
   ```bash
   cd ~/.openclaw/workspace/monitoring-console
   git config --global credential.helper osxkeychain
   ```

2. **推送**
   ```bash
   git push origin codex/develop-openclaw-multi-node-monitoring-console
   ```

3. **输入凭证**
   - macOS 会弹出对话框
   - Username: `sososong28-dev`
   - Password: **GitHub Personal Access Token**（不是密码！）

4. **获取 Token**
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 勾选 `repo` 权限
   - 生成后复制 token
   - 粘贴到密码框

---

### 方法 3：使用 Git Credential Manager

1. **安装 GCM**
   ```bash
   brew install git-credential-manager
   ```

2. **配置**
   ```bash
   git config --global credential.helper manager
   ```

3. **推送**
   ```bash
   cd ~/.openclaw/workspace/monitoring-console
   git push origin codex/develop-openclaw-multi-node-monitoring-console
   ```

4. **浏览器登录**
   - 会自动打开浏览器
   - 登录 GitHub
   - 授权 Git
   - 完成推送

---

### 方法 4：使用 SSH（如果你配置过 SSH 密钥）

1. **检查 SSH 密钥**
   ```bash
   ls -la ~/.ssh/id_rsa.pub
   ```

2. **如果密钥存在，切换为 SSH**
   ```bash
   cd ~/.openclaw/workspace/monitoring-console
   git remote set-url origin git@github.com:sososong28-dev/sososong.git
   git push origin codex/develop-openclaw-multi-node-monitoring-console
   ```

3. **如果密钥不存在，先配置 SSH**
   ```bash
   # 生成密钥
   ssh-keygen -t ed25519 -C "sososong28-dev@users.noreply.github.com"
   
   # 添加到 GitHub
   cat ~/.ssh/id_ed25519.pub
   # 复制输出内容到：https://github.com/settings/keys
   
   # 切换为 SSH 并推送
   git remote set-url origin git@github.com:sososong28-dev/sososong.git
   git push origin codex/develop-openclaw-multi-node-monitoring-console
   ```

---

## 推送成功后

推送成功后，访问 GitHub PR 页面查看更新：

https://github.com/sososong28-dev/sososong/pull/2

PR 会自动显示新的提交：
- `6087fe7 feat: 添加 OpenClaw 健康度仪表盘和 AI 会话记录`

---

## 快速命令参考

```bash
# 查看当前状态
cd ~/.openclaw/workspace/monitoring-console
git status

# 查看提交历史
git log --oneline -5

# 查看远程仓库
git remote -v

# 推送
git push origin codex/develop-openclaw-multi-node-monitoring-console

# 如果推送失败，查看错误
git push origin codex/develop-openclaw-multi-node-monitoring-console 2>&1 | tee push-error.log
```

---

## 需要帮助？

如果遇到问题，可以：

1. **查看 Git 配置**
   ```bash
   git config --list
   ```

2. **测试 GitHub 连接**
   ```bash
   # HTTPS
   curl -I https://github.com/sososong28-dev/sososong
   
   # SSH
   ssh -T git@github.com
   ```

3. **重置凭证**
   ```bash
   git credential-osxkeychain erase
   # 然后重新推送
   ```

---

_创建时间：2026-03-18 12:06_
