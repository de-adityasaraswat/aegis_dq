from datetime import datetime
from typing import Any, Optional
from aegis_dq.utils.logger import get_logger, trace_execution

log = get_logger(__name__)

class InMemoryStateStore:
    """Thread-safe in-memory store for watermarks."""
    def __init__(self):
        self._state = {}

    @trace_execution
    def get_watermark(self, table_name: str) -> Optional[datetime]:
        return self._state.get(table_name)

    @trace_execution
    def update_watermark(self, table_name: str, timestamp: datetime):
        log.info(f"Updating watermark for {table_name} to {timestamp}")
        self._state[table_name] = timestamp
