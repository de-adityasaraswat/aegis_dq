from pyspark.sql import SparkSession
from aegis_dq.core.engine import DQEngine
import datetime

spark = SparkSession.builder.appName("AegisProduction").getOrCreate()

# Complex production data
data = [
    (1, "Alice", 30, "active", datetime.datetime(2023, 1, 1)),
    (2, "Bob", 45, "inactive", datetime.datetime(2023, 5, 1)),
    (3, "Charlie", 120, "active", datetime.datetime(2023, 6, 1)),  # Age error
    (1, "Duplicate_ID", 20, "active", datetime.datetime(2023, 7, 1))  # Uniqueness error
]
df = spark.createDataFrame(data, ["id", "name", "age", "status", "updated_at"])

# Enterprise-grade configuration
config_json = {
    "checks": [
        # 1. Completeness Check
        {"type": "not_null", "column": "name", "name": "name_exists", "threshold_pct": 0},

        # 2. Uniqueness Check (Single Column)
        {"type": "unique", "column": "id", "name": "primary_key_integrity"},

        # 3. Categorical Integrity (Is in list)
        {"type": "is_in", "column": "status", "allowed_values": ["active", "inactive"], "name": "valid_status"},

        # 4. Type Safety Check
        {"type": "data_type", "column": "age", "expected_type": "integer", "name": "age_is_int"},

        # 5. Data Freshness (SLA Check)
        {"type": "freshness", "column": "updated_at", "max_age_days": 30, "name": "data_latency_check"}
    ]
}

engine = DQEngine()
results = engine.run(df, config_json, table_name="users")

import json

print(json.dumps(results, indent=4))
