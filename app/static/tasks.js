function getAuthHeaders() {
  return { 'X-API-Token': localStorage.getItem('apiToken') || '' };
}

async function loadTasks() {
  const response = await fetch('/api/tasks', { headers: getAuthHeaders() });
  if (!response.ok) throw new Error(`请求失败: ${response.status}`);
  const tasks = await response.json();
  const rows = document.getElementById('taskRows');
  rows.innerHTML = '';
  tasks.forEach(t => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${t.node_id}</td><td>${t.task_type}</td><td>${t.started_at}</td><td>${t.ended_at || '-'}</td><td>${t.status}</td><td>${t.error_message || '-'}</td>`;
    rows.appendChild(tr);
  });
}

loadTasks();
