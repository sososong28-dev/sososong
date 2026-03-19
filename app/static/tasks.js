function getAuthHeaders() {
  return { 'X-API-Token': localStorage.getItem('apiToken') || '' };
}

async function requestJson(url) {
  const response = await fetch(url, { headers: getAuthHeaders() });
  if (!response.ok) throw new Error(`请求失败: ${response.status}`);
  return response.json();
}

async function loadTasks() {
  const [tasks, usages] = await Promise.all([requestJson('/api/tasks'), requestJson('/api/token-usage')]);

  const rows = document.getElementById('taskRows');
  rows.innerHTML = '';
  tasks.forEach(t => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${t.node_id}</td><td>${t.task_type}</td><td>${t.started_at}</td><td>${t.ended_at || '-'}</td><td>${t.status}</td><td>${t.error_message || '-'}</td>`;
    rows.appendChild(tr);
  });

  const usageRows = document.getElementById('usageRows');
  usageRows.innerHTML = '';
  usages.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${item.node_id}</td><td>${item.provider}</td><td>${item.model_name}</td><td>${item.prompt_tokens}</td><td>${item.completion_tokens}</td><td>${item.total_tokens}</td><td>${item.recorded_at}</td>`;
    usageRows.appendChild(tr);
  });
}

loadTasks();
