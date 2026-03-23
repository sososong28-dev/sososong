from datetime import datetime
from uuid import uuid4


def new_trace_id() -> str:
    return f"{datetime.utcnow():%Y%m%d%H%M%S}-{uuid4().hex[:8]}"
