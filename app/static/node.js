function getAuthHeaders() {
  return { 'X-API-Token': localStorage.getItem('apiToken') || '' };
}

function renderTaskList(tasks) {
  const root = document.getElementById('tasks');
  root.innerHTML = '';
  tasks.forEach(task => {
    const li = document.createElement('li');
    li.className = 'list-item-card';
    li.innerHTML = `
      <strong>${task.task_type}</strong>
      <span>${task.status}</span>
      <div class="muted-text">开始：${task.started_at}</div>
      <div class="muted-text">结束：${task.ended_at || '-'}</div>
    `;
    root.appendChild(li);
  });
}

function renderLogList(logs) {
  const root = document.getElementById('logs');
  root.innerHTML = '';
  logs.forEach(log => {
    const li = document.createElement('li');
    li.className = 'list-item-card';
    li.innerHTML = `<strong>[${log.level}]</strong><div class="muted-text">${log.message}</div>`;
    root.appendChild(li);
  });
}

function renderTokenTable(items) {
  const tokenRows = document.getElementById('tokenRows');
  tokenRows.innerHTML = '';
  items.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${item.provider}</td><td>${item.model_name}</td><td>${item.prompt_tokens}</td><td>${item.completion_tokens}</td><td>${item.total_tokens}</td><td>${item.recorded_at}</td>`;
    tokenRows.appendChild(tr);
  });
}

async function loadNode() {
  const res = await fetch(`/api/nodes/${window.NODE_ID}`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`请求失败: ${res.status}`);
  const node = await res.json();
  document.getElementById('title').textContent = `${node.name} 详情`;
  document.getElementById('machine').textContent = JSON.stringify(
    {
      host: node.host,
      ip: node.ip,
      os_type: node.os_type,
      status: node.status,
      ssh_status: node.ssh_status,
      cpu: node.cpu_usage,
      memory: node.memory_usage,
      disk: node.disk_usage,
      openclaw_status: node.openclaw_status,
      listening_state: node.listening_state,
      last_probe_at: node.last_probe_at,
      last_token_total: node.last_token_total,
    },
    null,
    2,
  );
  document.getElementById('logSummary').textContent = node.last_log_summary || '-';
  renderLogList(node.logs);
  renderTokenTable(node.token_usage_records);
  renderTaskList(node.tasks);
}

document.getElementById('checkBtn').addEventListener('click', async () => {
  await fetch(`/api/nodes/${window.NODE_ID}/check`, { method: 'POST', headers: getAuthHeaders() });
  await loadNode();
});

loadNode();
