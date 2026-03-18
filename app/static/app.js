// API Token 配置
function getAuthHeaders() {
  const token = localStorage.getItem('apiToken') || '854d3d95aa57b9ab324ac4289de371cbcc99a58fac1072aa0f194e17a4e7b303';
  return { 'X-API-Token': token };
}

// 告警声音
function playAlert() {
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const oscillator = audioContext.createOscillator();
  const gainNode = audioContext.createGain();
  
  oscillator.connect(gainNode);
  gainNode.connect(audioContext.destination);
  
  oscillator.frequency.value = 800;
  oscillator.type = 'sine';
  gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
  gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
  
  oscillator.start(audioContext.currentTime);
  oscillator.stop(audioContext.currentTime + 0.5);
}

// 解析 OpenClaw 状态输出
function parseOpenClawStatus(stdout) {
  const result = {
    gateway: { status: 'unknown', port: null, reachable: false },
    telegram: { status: 'unknown', accounts: 0, enabled: false },
    sessions: { active: 0, total: 0 },
    security: { critical: 0, warn: 0, info: 0 },
    dashboard: { status: 'unknown', url: null },
    tasks: []
  };
  
  if (!stdout) return result;
  
  // 网关状态
  if (stdout.includes('Gateway:')) {
    if (stdout.includes('ws://')) {
      result.gateway.status = 'running';
      const portMatch = stdout.match(/:(\d+)/);
      result.gateway.port = portMatch ? portMatch[1] : '18789';
      result.gateway.reachable = !stdout.includes('unreachable');
    } else if (stdout.includes('unreachable')) {
      result.gateway.status = 'unreachable';
    }
  }
  
  // Dashboard URL
  const dashMatch = stdout.match(/Dashboard\s*\|\s*(http[^\|]+)/);
  if (dashMatch) {
    result.dashboard.url = dashMatch[1].trim();
    result.dashboard.status = 'available';
  }
  
  // Telegram 状态
  if (stdout.includes('Telegram') && stdout.includes('ON')) {
    result.telegram.enabled = true;
    result.telegram.status = 'connected';
    const accMatch = stdout.match(/accounts (\d+)\/(\d+)/);
    if (accMatch) {
      result.telegram.accounts = parseInt(accMatch[1]);
    }
  } else if (stdout.includes('Telegram') && stdout.includes('OFF')) {
    result.telegram.status = 'disabled';
  }
  
  // 会话数量
  const sessMatch = stdout.match(/Sessions?\s+(\d+)\s+active/);
  if (sessMatch) {
    result.sessions.active = parseInt(sessMatch[1]);
  }
  const sessTotalMatch = stdout.match(/sessions (\d+)/);
  if (sessTotalMatch) {
    result.sessions.total = parseInt(sessTotalMatch[1]);
  }
  
  // 安全审计
  const secMatch = stdout.match(/(\d+)\s+critical.*?(\d+)\s+warn.*?(\d+)\s+info/);
  if (secMatch) {
    result.security.critical = parseInt(secMatch[1]);
    result.security.warn = parseInt(secMatch[2]);
    result.security.info = parseInt(secMatch[3]);
  }
  
  return result;
}

// 解析会话列表输出
function parseSessionsList(stdout) {
  const sessions = [];
  if (!stdout) return sessions;
  
  const lines = stdout.split('\n');
  let inTable = false;
  
  for (const line of lines) {
    // 检测表格开始
    if (line.includes('Key') && line.includes('Kind')) {
      inTable = true;
      continue;
    }
    if (line.includes('───') || line.includes('═══')) {
      if (inTable) inTable = false; // 表格结束
      else continue; // 表格头部分隔线
    }
    
    if (inTable && line.trim() && line.includes('|')) {
      const parts = line.split('|').map(p => p.trim()).filter(p => p);
      if (parts.length >= 3) {
        const [key, kind, age, ...rest] = parts;
        sessions.push({
          key: key.substring(0, 30) + (key.length > 30 ? '...' : ''),
          kind: kind,
          age: age,
          model: rest[0] || '-',
          tokens: rest[1] || '-'
        });
      }
    }
  }
  
  return sessions;
}

// 解析 Memory 列表输出
function parseMemoryList(stdout) {
  const memories = [];
  if (!stdout) return memories;
  
  const lines = stdout.split('\n');
  for (const line of lines) {
    if (line.includes('memory/') && line.includes('.md')) {
      const match = line.match(/memory\/(\d{4}-\d{2}-\d{2})\.md/);
      if (match) {
        memories.push({
          date: match[1],
          file: line.trim()
        });
      }
    }
  }
  
  return memories;
}

// 计算健康度分数
function calculateHealthScore(status) {
  let score = 100;
  if (status.gateway.status === 'running' && status.gateway.reachable) score += 0;
  else score -= 30;
  if (status.telegram.enabled && status.telegram.accounts > 0) score += 0;
  else if (!status.telegram.enabled) score -= 10;
  else score -= 20;
  score -= status.security.critical * 10;
  score -= status.security.warn * 3;
  if (status.sessions.active > 0) score += 0;
  else score -= 10;
  if (status.dashboard.status === 'available') score += 0;
  else score -= 10;
  return Math.max(0, Math.min(100, score));
}

// 获取健康度信息
function getHealthInfo(score) {
  if (score >= 90) return { color: '#27ae60', text: '优秀', emoji: '😊' };
  if (score >= 70) return { color: '#2ecc71', text: '良好', emoji: '👍' };
  if (score >= 50) return { color: '#f39c12', text: '一般', emoji: '😐' };
  if (score >= 30) return { color: '#e67e22', text: '较差', emoji: '😟' };
  return { color: '#e74c3c', text: '严重', emoji: '😱' };
}

// 获取状态文本
function getStatusText(status) {
  const map = { 'online': '🟢 在线', 'offline': '🔴 离线', 'error': '🟠 异常', 'unknown': '⚪ 未知' };
  return map[status] || status;
}

function getOpenClawText(status) {
  const map = { 'running': '🟢 运行中', 'stopped': '⚪ 未运行', 'error': '🔴 错误', 'unknown': '⚪ 未知' };
  return map[status] || status;
}

function getMetricClass(value) {
  return value > 85 ? 'high' : '';
}

// 渲染节点卡片
function render(nodes) {
  const filter = document.getElementById('statusFilter').value;
  const list = document.getElementById('nodeList');
  list.innerHTML = '';
  
  const filtered = nodes.filter(n => filter === 'all' ? true : n.status === filter);
  let hasOffline = false;
  
  filtered.forEach(node => {
    const div = document.createElement('div');
    div.className = `card status-${node.status}`;
    
    const cpu = node.cpu_usage || 0, mem = node.memory_usage || 0, disk = node.disk_usage || 0;
    
    // 解析 OpenClaw 详细状态（如果有命令结果）
    const ocStatus = node._ocStatus || {};
    const healthScore = ocStatus.gateway ? calculateHealthScore(ocStatus) : null;
    const healthInfo = healthScore !== null ? getHealthInfo(healthScore) : null;
    
    div.innerHTML = `
      <h3>${node.name}</h3>
      <p><span class="status-badge">${getStatusText(node.status)}</span></p>
      <p>🖥️ ${node.host} (${node.os_type})</p>
      <p>🔧 OpenClaw: ${getOpenClawText(node.openclaw_status)}</p>
      
      ${healthInfo ? `
        <div style="margin:12px 0;padding:10px;background:#f8f9fa;border-radius:6px;border-left:3px solid ${healthInfo.color};">
          <p style="margin:0 0 8px;font-size:13px;font-weight:600;color:${healthInfo.color};">
            ${healthInfo.emoji} OpenClaw 健康度：${healthInfo.text} (${healthScore}分)
          </p>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px;">
            <span>🌐 网关：${ocStatus.gateway.status === 'running' ? '🟢' : '🔴'} ${ocStatus.gateway.port ? '端口'+ocStatus.gateway.port : ocStatus.gateway.status}</span>
            <span>📱 Telegram: ${ocStatus.telegram.enabled ? '🟢 '+ocStatus.telegram.accounts+'账号' : '⚪ 未启用'}</span>
            <span>💬 会话：${ocStatus.sessions.active}活跃</span>
            <span>🔒 安全：<span style="color:${getSecurityColor(ocStatus.security.critical, ocStatus.security.warn)}">${ocStatus.security.critical}严重 ${ocStatus.security.warn}警告</span></span>
          </div>
        </div>
      ` : ''}
      
      <div class="metrics">
        <div class="metric">
          <div class="metric-label"><span>CPU</span><span>${cpu.toFixed(1)}%</span></div>
          <div class="metric-bar"><div class="metric-fill cpu ${getMetricClass(cpu)}" style="width:${cpu}%"></div></div>
        </div>
        <div class="metric">
          <div class="metric-label"><span>内存</span><span>${mem.toFixed(1)}%</span></div>
          <div class="metric-bar"><div class="metric-fill memory ${getMetricClass(mem)}" style="width:${mem}%"></div></div>
        </div>
        <div class="metric">
          <div class="metric-label"><span>磁盘</span><span>${disk.toFixed(1)}%</span></div>
          <div class="metric-bar"><div class="metric-fill disk ${getMetricClass(disk)}" style="width:${disk}%"></div></div>
        </div>
      </div>
      
      <p style="margin-top:12px;font-size:12px;color:#718096;">
        🕐 最后心跳：${node.last_heartbeat_at ? new Date(node.last_heartbeat_at).toLocaleString('zh-CN') : '-'}
      </p>
    `;
    
    div.onclick = () => showNodeDetail(node);
    list.appendChild(div);
    
    if (node.status === 'offline' || node.status === 'error') hasOffline = true;
  });
  
  document.getElementById('lastRefresh').textContent = `最后刷新：${new Date().toLocaleString('zh-CN')}`;
  if (hasOffline && filtered.length > 0) playAlert();
}

// 显示节点详情
function showNodeDetail(node) {
  const modal = document.getElementById('nodeModal');
  const content = document.getElementById('modalContent');
  const ocStatus = node._ocStatus || {};
  const sessions = node._sessions || [];
  
  content.innerHTML = `
    <div class="modal-header">
      <h2>${node.name}</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    
    <div style="margin-bottom:20px;">
      <p><strong>ID:</strong> ${node.id}</p>
      <p><strong>主机:</strong> ${node.host} (${node.os_type})</p>
      <p><strong>IP:</strong> ${node.ip}</p>
      <p><strong>状态:</strong> ${getStatusText(node.status)}</p>
      <p><strong>OpenClaw:</strong> ${getOpenClawText(node.openclaw_status)}</p>
    </div>
    
    ${ocStatus.gateway ? `
      <h3 style="margin:20px 0 12px;">🥟 OpenClaw 详细状态</h3>
      <div style="background:#f8f9fa;padding:16px;border-radius:8px;">
        <h4 style="margin:0 0 12px;font-size:14px;color:#2d3748;">📊 健康度评分：${calculateHealthScore(ocStatus)}分 ${getHealthInfo(calculateHealthScore(ocStatus)).emoji}</h4>
        
        <table style="margin-bottom:16px;">
          <tr><th>🌐 网关</th><td>${ocStatus.gateway.status === 'running' ? '🟢 运行中' : '🔴 '+ocStatus.gateway.status} ${ocStatus.gateway.port ? '(端口 '+ocStatus.gateway.port+')' : ''}</td></tr>
          <tr><th>📱 Telegram</th><td>${ocStatus.telegram.enabled ? '🟢 已连接 ('+ocStatus.telegram.accounts+' 账号)' : '⚪ 未启用'}</td></tr>
          <tr><th>💬 会话</th><td>${ocStatus.sessions.active} 活跃 / ${ocStatus.sessions.total} 总计</td></tr>
          <tr><th>🔒 安全审计</th><td style="color:${getSecurityColor(ocStatus.security.critical, ocStatus.security.warn)}">${ocStatus.security.critical} 严重 / ${ocStatus.security.warn} 警告 / ${ocStatus.security.info} 信息</td></tr>
          <tr><th>🖥️ Dashboard</th><td>${ocStatus.dashboard.url ? '<a href="'+ocStatus.dashboard.url+'" target="_blank">'+ocStatus.dashboard.url+'</a>' : '不可用'}</td></tr>
        </table>
      </div>
    ` : ''}
    
    ${sessions.length > 0 ? `
      <h3 style="margin:20px 0 12px;">🤖 AI 会话记录（今日）</h3>
      <div style="background:#f0f4ff;padding:16px;border-radius:8px;max-height:400px;overflow-y:auto;">
        <table style="font-size:13px;">
          <thead>
            <tr>
              <th style="width:40%;">会话 Key</th>
              <th>类型</th>
              <th>最后活跃</th>
              <th>模型</th>
            </tr>
          </thead>
          <tbody>
            ${sessions.map(s => `
              <tr>
                <td style="font-family:monospace;font-size:12px;">${s.key}</td>
                <td>${getKindEmoji(s.kind)} ${s.kind}</td>
                <td>${s.age}</td>
                <td>${s.model}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <p style="margin-top:12px;font-size:12px;color:#718096;">
          📊 总计：${sessions.length} 个会话
        </p>
      </div>
    ` : ''}
    
    <h3 style="margin:20px 0 12px;">📊 系统指标</h3>
    <table>
      <tr><th>CPU</th><td>${node.cpu_usage !== null ? node.cpu_usage.toFixed(2)+'%' : '-'}</td></tr>
      <tr><th>内存</th><td>${node.memory_usage !== null ? node.memory_usage.toFixed(2)+'%' : '-'}</td></tr>
      <tr><th>磁盘</th><td>${node.disk_usage !== null ? node.disk_usage.toFixed(2)+'%' : '-'}</td></tr>
    </table>
    
    <div style="margin-top:20px;display:flex;gap:12px;flex-wrap:wrap;">
      <button class="export-btn" onclick="exportNodeData(${JSON.stringify(node).replace(/"/g, '&quot;')})">📥 导出数据</button>
      <button onclick="checkNode('${node.id}')" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;padding:8px 20px;border-radius:6px;cursor:pointer;">🔄 手动检查</button>
      <button onclick="runSecurityCommands('${node.id}')" style="background:linear-gradient(135deg,#27ae60,#2ecc71);color:white;border:none;padding:8px 20px;border-radius:6px;cursor:pointer;">🔒 执行安全命令</button>
    </div>
  `;
  
  modal.classList.add('active');
}

// 获取会话类型表情
function getKindEmoji(kind) {
  const map = {
    'direct': '💬',
    'group': '👥',
    'slash': '⚡',
    'channel': '📢'
  };
  return map[kind] || '📁';
}

function closeModal() {
  document.getElementById('nodeModal').classList.remove('active');
}

function exportNodeData(node) {
  const dataStr = JSON.stringify(node, null, 2);
  const blob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `node-${node.id}-${new Date().toISOString().split('T')[0]}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

async function checkNode(nodeId) {
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = '检查中...';
  try {
    const res = await fetch(`/api/nodes/${nodeId}/check`, { method: 'POST', headers: getAuthHeaders() });
    if (res.ok) { await load(); alert('✅ 检查完成'); }
    else alert('❌ 检查失败');
  } catch (err) { alert('❌ 请求失败：' + err.message); }
  finally { btn.disabled = false; btn.textContent = '🔄 手动检查'; }
}

async function runSecurityCommands(nodeId) {
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = '执行中...';
  try {
    const res = await fetch(`/api/nodes/${nodeId}/run-command`, { method: 'POST', headers: getAuthHeaders() });
    const data = await res.json();
    if (res.ok && data.commands) {
      // 解析健康命令（前 2 个）
      if (data.health && data.health[0] && data.health[0].success) {
        window._lastOcStatus = parseOpenClawStatus(data.health[1]?.stdout || data.health[0].stdout);
      }
      // 解析会话列表（task 命令的第一个）
      if (data.tasks && data.tasks[0] && data.tasks[0].success) {
        window._lastSessions = parseSessionsList(data.tasks[0].stdout);
      }
      showCommandResults(nodeId, data.commands);
    } else {
      alert('❌ 执行失败：' + (data.detail || '未知错误'));
    }
  } catch (err) { alert('❌ 请求失败：' + err.message); }
  finally { btn.disabled = false; btn.textContent = '🔒 执行安全命令'; }
}

function showCommandResults(nodeId, commands) {
  const modal = document.getElementById('nodeModal');
  const content = document.getElementById('modalContent');
  
  // 解析 OpenClaw 状态并存储
  if (commands[0] && commands[0].success) {
    const ocStatus = parseOpenClawStatus(commands[0].stdout);
    window._lastOcStatus = ocStatus;
    // 刷新列表显示健康度
    load();
  }
  
  let html = '';
  commands.forEach((cmd, i) => {
    const icon = cmd.success ? '✅' : '❌';
    const color = cmd.success ? '#27ae60' : '#e74c3c';
    html += `
      <div style="margin-bottom:16px;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;">
        <div style="background:#f7fafc;padding:8px 12px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center;">
          <code style="font-size:13px;color:#4a5568;">${i+1}. ${cmd.command}</code>
          <span style="color:${color};font-size:12px;font-weight:600;">${icon} 退出码：${cmd.exit_code}</span>
        </div>
        <div style="padding:12px;">
          ${cmd.stdout ? `<div style="margin-bottom:8px;"><strong style="color:#27ae60;font-size:12px;">✓ 输出:</strong><pre style="background:#f0fff4;padding:8px;border-radius:4px;font-size:12px;margin:4px 0;max-height:300px;overflow-y:auto;">${cmd.stdout}</pre></div>` : ''}
          ${cmd.stderr ? `<div><strong style="color:#e74c3c;font-size:12px;">✗ 错误:</strong><pre style="background:#fff5f5;padding:8px;border-radius:4px;font-size:12px;margin:4px 0;max-height:300px;overflow-y:auto;">${cmd.stderr}</pre></div>` : ''}
          ${!cmd.stdout && !cmd.stderr ? '<p style="color:#718096;font-size:12px;">无输出</p>' : ''}
        </div>
      </div>
    `;
  });
  
  content.innerHTML = `
    <div class="modal-header">
      <h2>🔒 安全命令执行结果</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div style="margin-bottom:20px;padding:12px;background:#e8f4fd;border-radius:6px;border-left:4px solid #3498db;">
      <p style="font-size:14px;color:#2c5282;margin:0;">💡 已执行 ${commands.length} 个命令，${commands.filter(c=>c.success).length} 个成功，${commands.filter(c=>!c.success).length} 个失败</p>
    </div>
    ${html}
    <div style="margin-top:20px;text-align:right;">
      <button onclick="runSecurityCommands('${nodeId}')" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;padding:10px 24px;border-radius:6px;cursor:pointer;font-weight:500;">🔄 重新执行</button>
    </div>
  `;
  
  modal.classList.add('active');
}

function exportAllData() {
  fetchNodes().then(nodes => {
    const dataStr = JSON.stringify(nodes, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `all-nodes-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });
}

async function fetchNodes() {
  const res = await fetch('/api/nodes', { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`请求失败：${res.status}`);
  return res.json();
}

async function load() {
  try {
    const nodes = await fetchNodes();
    // 如果有上次解析的 OpenClaw 状态，附加到节点上
    if (window._lastOcStatus) {
      const macNode = nodes.find(n => n.id === 'mac-openclaw-master');
      if (macNode) macNode._ocStatus = window._lastOcStatus;
    }
    // 如果有会话数据，附加到节点上
    if (window._lastSessions) {
      const macNode = nodes.find(n => n.id === 'mac-openclaw-master');
      if (macNode) macNode._sessions = window._lastSessions;
    }
    render(nodes);
    document.getElementById('error').textContent = '';
  } catch (err) {
    document.getElementById('error').textContent = String(err.message || err);
  }
}

// 初始化
document.getElementById('refreshBtn').addEventListener('click', load);
document.getElementById('statusFilter').addEventListener('change', load);
document.getElementById('exportBtn').addEventListener('click', exportAllData);
document.getElementById('saveTokenBtn').addEventListener('click', () => {
  localStorage.setItem('apiToken', document.getElementById('tokenInput').value.trim());
  load();
  alert('✅ Token 已保存');
});
document.getElementById('tokenInput').value = localStorage.getItem('apiToken') || '';
document.getElementById('nodeModal').addEventListener('click', (e) => {
  if (e.target.id === 'nodeModal') closeModal();
});

load();
setInterval(load, (window.REFRESH_SECONDS || 15) * 1000);
