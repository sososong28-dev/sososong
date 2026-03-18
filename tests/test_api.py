AUTH = {'X-API-Token': 'test-token'}


def test_health(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'


def test_nodes_list(client):
    res = client.get('/api/nodes', headers=AUTH)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3


def test_auth_required(client):
    res = client.get('/api/nodes')
    assert res.status_code == 401


def test_node_detail(client):
    res = client.get('/api/nodes/mac-openclaw-master', headers=AUTH)
    assert res.status_code == 200
    assert res.json()['id'] == 'mac-openclaw-master'


def test_node_id_validation(client):
    res = client.get('/api/nodes/../etc/passwd', headers=AUTH)
    assert res.status_code in (404, 422)


def test_tasks(client):
    check = client.post('/api/nodes/mac-openclaw-master/check', headers=AUTH)
    assert check.status_code == 200
    res = client.get('/api/tasks', headers=AUTH)
    assert res.status_code == 200
    assert len(res.json()) >= 1
