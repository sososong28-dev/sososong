from app.probe import ALLOWED_ACTIONS, summarize_logs


def test_action_whitelist():
    assert 'health_check' in ALLOWED_ACTIONS
    assert 'fetch_logs' in ALLOWED_ACTIONS
    assert 'check_process' in ALLOWED_ACTIONS


def test_summarize_logs(tmp_path):
    p = tmp_path / 'a.log'
    p.write_text('line1\nline2\n', encoding='utf-8')
    out = summarize_logs(str(p))
    assert 'line1' in out
