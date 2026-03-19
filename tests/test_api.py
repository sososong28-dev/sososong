AUTH = {'X-API-Token': 'test-token'}


def test_health(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'


def test_nodes_list(client):
    client.post('/api/nodes/check-all', headers=AUTH)
    res = client.get('/api/nodes', headers=AUTH)
    assert res.status_code == 200
    data = res.json()
    assert data['summary']['total_nodes'] == 3
    assert data['summary']['windows_nodes'] == 2
    assert len(data['nodes']) == 3


def test_auth_required(client):
    res = client.get('/api/nodes')
    assert res.status_code == 401


def test_node_detail(client):
    client.post('/api/nodes/mac-openclaw-master/check', headers=AUTH)
    res = client.get('/api/nodes/mac-openclaw-master', headers=AUTH)
    assert res.status_code == 200
    assert res.json()['id'] == 'mac-openclaw-master'
    assert len(res.json()['token_usage_records']) >= 1


def test_node_id_validation(client):
    res = client.get('/api/nodes/../etc/passwd', headers=AUTH)
    assert res.status_code in (404, 422)


def test_tasks_and_token_usage(client):
    check = client.post('/api/nodes/mac-openclaw-master/check', headers=AUTH)
    assert check.status_code == 200
    tasks = client.get('/api/tasks', headers=AUTH)
    usage = client.get('/api/token-usage', headers=AUTH)
    assert tasks.status_code == 200
    assert usage.status_code == 200
    assert len(tasks.json()) >= 1
    assert len(usage.json()) >= 1
