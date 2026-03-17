async function loadNode() {
  const res = await fetch(`/api/nodes/${window.NODE_ID}`);
  const node = await res.json();
  document.getElementById('title').textContent = `${node.name} 详情`;
  document.getElementById('machine').textContent = JSON.stringify({
    host: node.host,
    ip: node.ip,
    os_type: node.os_type,
    status: node.status,
    ssh_status: node.ssh_status,
    cpu: node.cpu_usage,
    memory: node.memory_usage,
    disk: node.disk_usage,
    openclaw_status: node.openclaw_status,
    last_probe_at: node.last_probe_at,
  }, null, 2);

  const logs = document.getElementById('logs');
  logs.innerHTML = '';
  node.logs.forEach(log => {
    const li = document.createElement('li');
    li.textContent = `[${log.level}] ${log.message}`;
    logs.appendChild(li);
  });

  const tasks = document.getElementById('tasks');
  tasks.innerHTML = '';
  node.tasks.forEach(task => {
    const li = document.createElement('li');
    li.textContent = `${task.task_type} - ${task.status} (${task.started_at})`;
    tasks.appendChild(li);
  });
}

document.getElementById('checkBtn').addEventListener('click', async () => {
  await fetch(`/api/nodes/${window.NODE_ID}/check`, { method: 'POST' });
  await loadNode();
});

loadNode();
