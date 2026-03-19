from app.database import SessionLocal
from app.models import Node, TokenUsageRecord


def test_db_read_write(client):
    db = SessionLocal()
    try:
        node = db.get(Node, 'mac-openclaw-master')
        node.status = 'online'
        db.add(TokenUsageRecord(node_id=node.id, provider='openai', model_name='gpt-4.1', total_tokens=99))
        db.commit()
        db.refresh(node)
        assert node.status == 'online'
        assert db.query(TokenUsageRecord).count() >= 1
    finally:
        db.close()
