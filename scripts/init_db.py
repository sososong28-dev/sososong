from app.database import Base, engine
from app.main import sync_nodes


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    sync_nodes()
    print('database initialized')
