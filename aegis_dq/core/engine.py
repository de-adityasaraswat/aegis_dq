from typing import Dict, Any
from aegis_dq.models.schemas import DQConfig
from aegis_dq.core.registry import CheckRegistry
from aegis_dq.utils.logger import get_logger
from aegis_dq.interfaces.base import MetadataSinkInterface, AlertManagerInterface
import inspect

log = get_logger(__name__)


class DQEngine:
    def __init__(self, sink: MetadataSinkInterface = None,
                 alert_manager: AlertManagerInterface = None
                 ):
        """
                Dependency Injection: The engine accepts ANY implementation
                of the Sink and Alert interfaces.
                """
        self.sink = sink
        self.alert_manager = alert_manager
        # --- THE FIX: Dynamic Package Discovery ---
        # We use inspect to find the absolute path of the 'aeg_dq' package
        # regardless of whether you run as 'python main.py' or 'python -m aeg_dq.main'
        try:
            # Get the module of this current class
            current_module = inspect.getmodule(self.__class__)
            package_root = current_module.__name__.split('.')[0]

            # Construct the path to the executors folder dynamically
            # This will result in 'aeg_dq.executors' automatically
            plugin_path = f"{package_root}.executors"

            log.info(f"Engine initialized. Auto-discovering plugins in: {plugin_path}")
            CheckRegistry.discover_plugins(plugin_path)
        except Exception as e:
            log.error(f"Failed to auto-discover plugins: {e}")
            # We don't crash the engine, we just allow it to run with built-ins only

    def run(self, df, config_input: Dict, table_name: str) -> Dict:
        # 1. Secure Validation of Input JSON via Pydantic
        try:
            config = DQConfig(**config_input)
        except Exception as e:
            log.error(f"Configuration Validation Failed: {e}")
            return {"status": "CRITICAL_ERROR", "error": str(e)}

        results = {}

        # 2. Iterative Execution with Error Isolation
        for check in config.checks:
            # IMPORTANT: 'check' is now a Pydantic Object.
            # We must use DOT notation (check.type), NOT bracket notation (check['type'])
            check_type = check.type
            check_name = check.name

            executor_cls = CheckRegistry.get_executor(check_type)
            if not executor_cls:
                log.error(f"No plugin for type: {check_type}")
                continue

            try:
                log.info(f"Running check: {check_name}")
                executor = executor_cls()
                # Pass the individual check object (already validated by Pydantic)
                results[check_name] = executor.execute(df, check)
            except Exception as e:
                log.error(f"Check '{check_name}' crashed: {str(e)}")
                results[check_name] = {"status": "ERROR", "error": str(e)}

        # After execution, we use the injected sink
        if self.sink:
            self.sink.write_results(table_name, results)
        # Use the injected alert manager
        if "FAIL" in str(results) and self.alert_manager:
            self.alert_manager.notify(f"DQ Failure in {table_name}", level="ERROR")

        return results
