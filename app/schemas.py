from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LogEvent(BaseModel):
    timestamp: datetime
    service: str
    host: str
    level: str
    message: str
    latency_ms: int
    trace_id: Optional[str] = None