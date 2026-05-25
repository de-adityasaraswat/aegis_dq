from pyspark.sql import functions as F
from aegis_dq.core.registry import CheckRegistry
from abc import ABC, abstractmethod
from typing import Any
import datetime


class BaseExecutor(ABC):
    @abstractmethod
    def execute(self, df, config: Any) -> dict: pass


@CheckRegistry.register_executor("not_null")
class NotNullExecutor(BaseExecutor):
    def execute(self, df, config):
        total = df.count()
        if total == 0: return {"status": "PASS"}
        nulls = df.filter(F.col(config.column).isNull()).count()
        pct = (nulls / total) * 100
        return {"status": "PASS" if pct <= config.threshold_pct else "FAIL", "null_pct": pct}


@CheckRegistry.register_executor("regex")
class RegexExecutor(BaseExecutor):
    def execute(self, df, config):
        invalid = df.filter(~F.col(config.column).rlike(config.pattern)).count()
        return {"status": "PASS" if invalid == 0 else "FAIL", "invalid_count": invalid}


@CheckRegistry.register_executor("schema_drift")
class SchemaDriftExecutor(BaseExecutor):
    def execute(self, df, config):
        actual = set(df.columns)
        expected = set(config.expected_columns)
        missing = expected - actual
        return {"status": "PASS" if not missing else "FAIL", "missing": list(missing)}


@CheckRegistry.register_executor("custom_python")
class CustomPythonExecutor(BaseExecutor):
    def execute(self, df, config) -> dict:
        # USE DOT NOTATION HERE!
        func_name = config.function_name

        try:
            func = CheckRegistry.get_func(func_name)
            return func(df, config)
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}


@CheckRegistry.register_executor("unique")
class UniqueExecutor(BaseExecutor):
    def execute(self, df, config) -> dict:
        total = df.count()
        distinct = df.select(config.column).distinct().count()
        is_pass = total == distinct
        return {"status": "PASS" if is_pass else "FAIL", "duplicates": total - distinct}


@CheckRegistry.register_executor("multi_unique")
class MultiUniqueExecutor(BaseExecutor):
    def execute(self, df, config) -> dict:
        total = df.count()
        # Count rows where the combination of columns is unique
        distinct = df.select(config.columns).distinct().count()
        is_mult_pass = total == distinct
        return {"status": "PASS" if is_mult_pass else "FAIL", "duplicates": total - distinct}


@CheckRegistry.register_executor("is_in")
class IsInExecutor(BaseExecutor):
    def execute(self, df, config) -> dict:
        # Check if values in column are within the allowed list
        invalid = df.filter(~F.col(config.column).isin(config.allowed_values)).count()
        return {"status": "PASS" if invalid == 0 else "FAIL", "invalid_count": invalid}


@CheckRegistry.register_executor("data_type")
class DataTypeExecutor(BaseExecutor):
    def execute(self, df, config) -> dict:
        # Use Spark's schema to validate type
        actual_type = df.schema[config.column].dataType.simpleString()
        # Simple mapping for demonstration (e.int, string, etc)
        is_pass = config.expected_type.lower() in actual_type.lower()
        return {"status": "PASS" if is_pass else "FAIL", "actual_type": actual_type}


@CheckRegistry.register_executor("freshness")
class FreshnessExecutor(BaseExecutor):
    def execute(self, df, config) -> dict:
        # Check if the max timestamp in column is within the allowed age
        max_date = df.select(F.max(config.column)).collect()[0][0]
        if not max_date: return {"status": "ERROR", "message": "No data found"}

        age_delta = datetime.datetime.now() - max_date
        is_pass = age_delta.days <= config.max_age_days
        return {
            "status": "PASS" if is_pass else "FAIL",
            "age_days": age_delta.days
        }
