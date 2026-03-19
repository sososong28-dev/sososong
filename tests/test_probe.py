from app.probe import ALLOWED_ACTIONS, extract_token_usage, summarize_logs


def test_action_whitelist():
    assert 'health_check' in ALLOWED_ACTIONS
    assert 'fetch_logs' in ALLOWED_ACTIONS
    assert 'check_process' in ALLOWED_ACTIONS


def test_summarize_logs(tmp_path):
    p = tmp_path / 'a.log'
    p.write_text('line1\nline2\n', encoding='utf-8')
    out = summarize_logs(str(p))
    assert 'line1' in out


def test_extract_token_usage():
    lines = [
        'provider=openai model=gpt-4o prompt_tokens=111 completion_tokens=22 total_tokens=133',
        'no tokens here',
    ]
    records = extract_token_usage(lines)
    assert len(records) == 1
    assert records[0]['provider'] == 'openai'
    assert records[0]['total_tokens'] == 133
