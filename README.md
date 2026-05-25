# 🛡️ AegisDQ 

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework: Spark](https://img.shields.io/badge/framework-PySpark-orange)](https://spark.apache.org/)

**AegisDQ** is an enterprise-grade data observability framework designed for high-scale, production-critical data pipelines. It provides the structural integrity required to ensure that your data is not just "valid," but trustworthy.

## ✨ Key Features

*   🚀 **Plugin-Driven Architecture**: Add new check logic simply by dropping a Python file into the `executors/` directory. No engine changes required.
*   💉 **Dependency Injection**: Fully decoupled architecture. Implement your own `MetadataSink` (e._g., Delta Lake, Postgres_) and `AlertManager` (e.g., Slack, PagerDuty) via standard interfaces.
*   🛡️ **Security-First Design**: Replaces unsafe `exec()` string execution with a structured `Runtime Function Registry`, protecting your pipeline from injection attacks.
*   ⚡ **Parallel Execution Engine**: Leverages multi-threading to execute hundreds of validation checks concurrently, minimizing the "Data Quality Tax" on your Spark jobs.
*   🛑 **Circuit Breaker Pattern**: Protect downstream consumers by automatically halting pipelines when critical data integrity violations are detected.
*   🔍 **Deep Observability**: Integrated `ContextVar` tracing ensures every log line identifies exactly which module and method triggered the event.

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/your-org/aegis_dq.git
cd aeg_dq
pip install -r requirements.txt
```
### Basic Uasage
```python
from aeg_dq.core.engine import DQEngine
from aeg_transformer.storage.state_manager import InMemoryStateStore
from aeg_dq.alerts.slack_adapter import SlackAlertManager # Your custom implementation

# 1. Initialize with your custom infrastructure
engine = DQEngine(
    sink=MyDeltaSink(), 
    alert_manager=SlackAlertManager()
)

# 2. Define your checks (JSON/Dict)
config = {
    "checks": [
        {"type": "not_null", "column": "user_id", "name": "id_exists", "threshold_pct": 0},
        {"type": "unique", "column": "email", "name": "unique_email"}
    ]
}

# 3. Run validation
results = engine.run(df, config, table_name="production_users")

```
### 🏗️ Architecture Overview
AegisDQ follows a strict separation of concerns:

- core/: The immutable orchestration engine and plugin registry.
- models/: Pydantic-powered contract definitions that validate configuration at the gate.
- executors/: The extensible library of data validators (The "Plugins").
- interfaces/: Abstract Base Classes defining how Sinks and Alerting must behave.
- utils/: Context-aware logging and observability tools.

### 🛠️ Developing Custom Checks
To add a new check, simply create a class in the exec_dq/executors/ folder:
```python
from aeg_dq.core.registry import CheckRegistry
from aeg_dq.core.base import BaseExecutor

@CheckRegistry.register_executor("my_new_check")
class MyNewCheck(BaseExecutor):
    def execute(self, df, config):
        # Your logic here...
        return {"status": "PASS"}

```
### 📜 License
MIT License - See LICENSE for details.


