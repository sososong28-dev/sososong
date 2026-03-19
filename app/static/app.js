function getAuthHeaders() {
  const token = localStorage.getItem('apiToken') || '';
  return { 'X-API-Token': token };
}

function formatPercent(value) {
  return `${Math.max(0, Math.min(100, Math.round(value || 0)))}%`;
}

function formatTokenValue(value) {
  return Number(value || 0).toLocaleString('zh-CN');
}

async function requestNodes(url = '/api/nodes', options = {}) {
  const res = await fetch(url, { ...options, headers: { ...getAuthHeaders(), ...(options.headers || {}) } });
  if (!res.ok) throw new Error(`请求失败: ${res.status}`);
  return res.json();
}

function renderSummary(summary) {
  const root = document.getElementById('summaryCards');
  root.innerHTML = '';
  const items = [
    { label: 'AGENT 总数', value: summary.total_nodes, hint: '已接入控制台的节点数量' },
    { label: 'Windows 节点', value: summary.windows_nodes, hint: 'Win1 / Win2 远程探测节点' },
    { label: '在线节点', value: summary.online_nodes, hint: '当前可用节点数量' },
    { label: '警告节点', value: summary.warning_nodes, hint: '进程停止或状态异常' },
  ];
  items.forEach(item => {
    const card = document.createElement('div');
    card.className = 'summary-card';
    card.innerHTML = `
      <div class="summary-label">${item.label}</div>
      <div class="summary-value">${item.value}</div>
      <div class="summary-hint">${item.hint}</div>
    `;
    root.appendChild(card);
  });

  const onlineRate = summary.total_nodes ? (summary.online_nodes / summary.total_nodes) * 100 : 0;
  const tokenRate = Math.min(100, summary.total_tokens / 50);
  document.getElementById('onlineRate').textContent = formatPercent(onlineRate);
  document.getElementById('onlineRateBar').style.width = `${onlineRate}%`;
  document.getElementById('totalTokensLabel').textContent = formatTokenValue(summary.total_tokens);
  document.getElementById('tokenRateBar').style.width = `${tokenRate}%`;

  document.getElementById('railNodeStatus').innerHTML = `
    <div class="metric-chip">在线 ${summary.online_nodes}</div>
    <div class="metric-chip">离线 ${summary.offline_nodes}</div>
    <div class="metric-chip">警告 ${summary.warning_nodes}</div>
  `;
  document.getElementById('railInsights').innerHTML = `
    <div class="rail-item">累计 Token：${formatTokenValue(summary.total_tokens)}</div>
    <div class="rail-item">Windows 节点：${summary.windows_nodes}</div>
    <div class="rail-item">可巡检总节点：${summary.total_nodes}</div>
  `;
}

function renderNodes(nodes) {
  const filter = document.getElementById('statusFilter').value;
  const list = document.getElementById('nodeList');
  list.innerHTML = '';
  nodes
    .filter(node => (filter === 'all' ? true : node.status === filter))
    .forEach(node => {
      const div = document.createElement('div');
      div.className = `card agent-card status-${node.status}`;
      div.dataset.testid = 'node-card';
      div.innerHTML = `
        <div class="agent-top">
          <div>
            <div class="agent-role">${node.os_type === 'windows' ? 'Windows Node' : 'Master Node'}</div>
            <h3>${node.name}</h3>
          </div>
          <span class="status-pill ${node.status}">${node.status}</span>
        </div>
        <div class="agent-meta">${node.host} · ${node.ip}</div>
        <div class="agent-stats">
          <div><span>OpenClaw</span><strong>${node.openclaw_status}</strong></div>
          <div><span>SSH</span><strong>${node.ssh_status}</strong></div>
          <div><span>监听</span><strong>${node.listening_state || '-'}</strong></div>
          <div><span>Token</span><strong>${formatTokenValue(node.last_token_total)}</strong></div>
        </div>
        <div class="agent-footnote">最近心跳：${node.last_heartbeat_at || '-'} </div>
        <div class="agent-footnote">最近错误：${node.last_error || '无'} </div>
      `;
      div.onclick = () => {
        window.location.href = `/nodes/${node.id}`;
      };
      list.appendChild(div);
    });
}

async function load() {
  try {
    const payload = await requestNodes();
    renderSummary(payload.summary);
    renderNodes(payload.nodes);
    document.getElementById('lastRefresh').textContent = `最后刷新: ${new Date().toLocaleString()}`;
    document.getElementById('error').textContent = '';
  } catch (err) {
    document.getElementById('error').textContent = String(err.message || err);
  }
}

async function checkAll() {
  try {
    const payload = await requestNodes('/api/nodes/check-all', { method: 'POST' });
    renderSummary(payload.summary);
    renderNodes(payload.nodes);
    document.getElementById('lastRefresh').textContent = `全量巡检完成: ${new Date().toLocaleString()}`;
    document.getElementById('error').textContent = '';
  } catch (err) {
    document.getElementById('error').textContent = String(err.message || err);
  }
}

document.getElementById('refreshBtn').addEventListener('click', load);
document.getElementById('checkAllBtn').addEventListener('click', checkAll);
document.getElementById('statusFilter').addEventListener('change', load);
document.getElementById('saveTokenBtn').addEventListener('click', () => {
  localStorage.setItem('apiToken', document.getElementById('tokenInput').value.trim());
  load();
});

document.getElementById('tokenInput').value = localStorage.getItem('apiToken') || '';
load();
setInterval(load, (window.REFRESH_SECONDS || 15) * 1000);
