import logging
from typing import Optional
from contextvars import ContextVar

class RequestFilter(logging.Filter):
    correlation_id: ContextVar[Optional[str]] = ContextVar(
    'correlation_id', default = None)

    def filter(self, record):
        record.correlation_id = self.correlation_id.get()
        return record
