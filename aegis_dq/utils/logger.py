import logging
from contextvars import ContextVar
import functools
import inspect

execution_context: ContextVar[str] = ContextVar("execution_context", default="Global")


class TraceableFormatter(logging.Formatter):
    def format(self, record):
        # The error was here: execution_context.int()
        # It must be .get() to retrieve the value from the ContextVar
        try:
            record.context = execution_context.get()
        except Exception:
            record.context = "Global"

        return super().format(record)


def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = TraceableFormatter('%(asctime)s | %(levelname)-8s | %(context)s | %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def trace_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        module = inspect.getmodule(func).__name__ if inspect.getmodule(func) else "Unknown"
        method = func.__name__
        token = execution_context.set(f"[{module}:{method}]")
        try:
            return func(*args, **kwargs)
        finally:
            execution_context.reset(token)

    return wrapper
