import importlib
import pkgutil
from typing import Dict, Type, Callable, Any

class CheckRegistry:
    _executors: Dict[str, Type] = {}
    _runtime_funcs: Dict[str, Callable] = {}

    @classmethod
    def register_executor(cls, check_type: str):
        """Decorator for built-in class-based checks."""
        def wrapper(executor_class: Type):
            cls._executors[check_type] = executor_class
            return executor_class
        return wrapper

    @classmethod
    def register_runtime_func(cls, name: str, func: Callable):
        """The Secure Extension Point for user-defined Python logic."""
        if not callable(func):
            raise TypeError(f"Registered object '{name}' is not a function.")
        cls._runtime_funcs[name] = func

    @classmethod
    def get_executor(cls, check_type: str) -> Type:
        return cls._executors.get(check_type)

    @classmethod
    def get_func(cls, name: str) -> Callable:
        if name not in cls._runtime_funcs:
            raise KeyError(f"Runtime function '{name}' not found in Aegis Registry.")
        return cls._runtime_funcs[name]

    @classmethod
    def discover_plugins(cls, package_path: str):
        """Scans the executors folder and imports all modules."""
        package = importlib.import_module(package_path)
        for _, modname, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            importlib.import_module(modname)
