import datetime
from pyspark.sql import SparkSession
# Import the interfaces from YOUR library
from aegis_dq.interfaces.base import MetadataSinkInterface, AlertManagerInterface
from aegis_dq.core.engine import DQEngine


# --- CUSTOMER IMPLEMENTATION 1: Slack Alerter ---
class SlackAlertManager(AlertManagerInterface):
    def notify(self, message: str, level: str) -> None:
        # In real life, this would use 'requests' to hit a Webhook URL
        print(f"🚀 [SLACK NOTIFICATION] [{level}] 📢 {message}")


# --- CUSTOM_IMPLEMENTATION 2: Delta Lake Sink ---
class DeltaLakeSink(MetadataSinkInterface):
    def write_results(self, table_name: str, results: Dict) -> None:
        print(f"💾 [DELTA LAKE] Writing results for {table_name} to s3://my-bucket/dq_logs/")
        # Implementation would use spark.write.format("delta").save(...)


# --- THE PIPELINE EXECUTION ---
def main():
    spark = SparkSession.builder.appName("CustomerPipeline").getOrCreate()

    # The customer creates their OWN custom tools
    my_slack_plugin = SlackAlertManager()
    my_delta_plugin = DeltaLakeSink()

    # The engine is initialized with the CUSTOMER'S tools (Dependency Injection)
    engine = DQEngine(sink=my_delta_plugin, alert_manager=my_slack_plugin)

    # Run the pipeline
    df = spark.read.table("production_users")
    config = {"checks": [...]}  # Standard config

    engine.run(df, config, table_name="users")


if __name__ == "__main__":
    main()
