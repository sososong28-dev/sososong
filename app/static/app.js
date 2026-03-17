async function fetchNodes() {
  const res = await fetch('/api/nodes');
  return res.json();
}

function render(nodes) {
  const filter = document.getElementById('statusFilter').value;
  const list = document.getElementById('nodeList');
  list.innerHTML = '';
  nodes.filter(n => filter === 'all' ? true : n.status === filter).forEach(node => {
    const div = document.createElement('div');
    div.className = `card status-${node.status}`;
    div.dataset.testid = 'node-card';
    div.innerHTML = `
      <h3>${node.name}</h3>
      <p>机器: ${node.host} (${node.os_type})</p>
      <p>状态: <span>${node.status}</span></p>
      <p>OpenClaw: ${node.openclaw_status}</p>
      <p>最近心跳: ${node.last_heartbeat_at || '-'}</p>
      <p>最近错误: ${node.last_error || '-'}</p>
    `;
    div.onclick = () => { window.location.href = `/nodes/${node.id}`; };
    list.appendChild(div);
  });
  document.getElementById('lastRefresh').textContent = `最后刷新: ${new Date().toLocaleString()}`;
}

async function load() {
  const nodes = await fetchNodes();
  render(nodes);
}

document.getElementById('refreshBtn').addEventListener('click', load);
document.getElementById('statusFilter').addEventListener('change', load);
load();
setInterval(load, (window.REFRESH_SECONDS || 15) * 1000);
