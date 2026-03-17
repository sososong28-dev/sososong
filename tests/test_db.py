from app.database import SessionLocal
from app.models import Node


def test_db_read_write(client):
    db = SessionLocal()
    try:
        node = db.get(Node, 'mac-openclaw-master')
        node.status = 'online'
        db.commit()
        db.refresh(node)
        assert node.status == 'online'
    finally:
        db.close()
