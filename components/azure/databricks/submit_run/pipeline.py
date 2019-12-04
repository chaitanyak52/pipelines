"""Submit a one-time Run with implicit cluster creation to Databricks."""
import os
import kfp
from kfp import dsl

def submit_run(run_name, parameter):
    component_root = os.path.dirname(os.path.abspath(__file__))
    databricks_submit_run_op = kfp.components.load_component(os.path.join(component_root, 'component.yaml'))
    return databricks_submit_run_op(
        run_name=run_name,
        new_cluster={
            "spark_version": "5.3.x-scala2.11",
            "node_type_id": "Standard_D3_v2",
            "num_workers": 2
        },
        libraries=[{"jar": "dbfs:/docs/sparkpi.jar"}],
        spark_jar_task={
            "main_class_name": "org.apache.spark.examples.SparkPi",
            "parameters": [parameter]
        }
    )

@dsl.pipeline(
    name="DatabricksRun",
    description="A toy pipeline that computes an approximation to pi with Azure Databricks."
)
def calc_pipeline(run_name="test-run", parameter="10"):
    submit_run_task = submit_run(run_name, parameter)

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(calc_pipeline, __file__ + ".tar.gz")
