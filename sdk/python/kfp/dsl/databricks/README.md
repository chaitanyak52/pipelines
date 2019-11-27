# Introduction to Databricks DSL 

Databricks DSL provides a set of [Kubeflow Pipeline](https://www.kubeflow.org/docs/pipelines/) Tasks
(Ops) which let us manipulate [Azure Databricks](https://azure.microsoft.com/services/databricks/) 
resources using the [Azure Databricks Operator for Kubernetes](
https://github.com/microsoft/azure-databricks-operator).

These are the supported Ops up to date:

- CreateClusterOp, to create a Databricks cluster in Azure Databricks.
- DeleteClusterOp, to delete a Databricks cluster from Azure Databricks.
- CreateJobOp, to create a Spark Job in Azure Databricks.
- DeleteJobOp, to delete a Spark Job from Azure Databricks.
- SubmitRunOp, to submit a one-time Job Run in Azure Databricks.

SubmitRunOp is the most complete of them all, as we can create the Op by using the complete 
Databricks spec as a Python dictionary or its individual parts as named parameters. It also 
provides 2 helper methods to create the Op by using a json string containing the spec or a file name
containing the spec in json format. The rest of the Ops only support passing the complete Databricks
spec as a Python dictionary for now.

## Setup

1) [Create an Azure Databricks workspace](
    https://docs.microsoft.com/en-us/azure/databricks/getting-started/try-databricks?toc=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Fazure-databricks%2FTOC.json&bc=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Fbread%2Ftoc.json#--step-2-create-an-azure-databricks-workspace)
2) [Deploy the Azure Databricks Operator for Kubernetes](
    https://github.com/microsoft/azure-databricks-operator/blob/master/docs/deploy.md)
3) [Install the Kubeflow Pipelines SDK](https://www.kubeflow.org/docs/pipelines/sdk/install-sdk/)

## Examples

The following sample pipeline will submit a one-time job run with implicit cluster creation to Azure 
Databricks:

```python
import kfp.dsl as dsl
import kfp.dsl.databricks as databricks

@dsl.pipeline(
    name="DatabricksRun",
    description="A toy pipeline that computes an approximation to pi with Azure Databricks."
)
def calc_pipeline(run_name="test-run", parameter="10"):
    databricks.SubmitRunOp(
        name="submitrun",
        run_name=run_name,
        new_cluster={
            "spark_version":"5.3.x-scala2.11",
            "node_type_id": "Standard_D3_v2",
            "num_workers": 2
        },
        libraries=[{"jar": "dbfs:/docs/sparkpi.jar"}],
        spark_jar_task={
            "main_class_name": "org.apache.spark.examples.SparkPi",
            "parameters": [parameter]
        }
    )
```

This sample is based on the following article: [Create a spark-submit job](
https://docs.databricks.com/dev-tools/api/latest/examples.html#create-and-run-a-jar-job), which 
points to the library *sparkpi.jar*. You may upload the library to [Databricks 
File System](https://docs.microsoft.com/en-us/azure/databricks/data/databricks-file-system) using 
[DBFS CLI](https://docs.microsoft.com/en-us/azure/databricks/dev-tools/databricks-cli#dbfs-cli).

More sample pipelines can be found in the tests folder of the Databricks DSL: 
[pipelines/sdk/python/tests/dsl/databricks](../../../tests/dsl/databricks)

## Additional information
- [Kubeflow Pipelines](https://www.kubeflow.org/docs/pipelines/) 
- [Azure Databricks documentation](https://docs.microsoft.com/azure/azure-databricks/) 
- [Azure Databricks Operator for Kubernetes](https://github.com/microsoft/azure-databricks-operator)
- [Golang SDK for DataBricks REST API 2.0 and Azure DataBricks REST API 2.0](
    https://github.com/xinsnake/databricks-sdk-golang), used by Azure Databricks Operator.
- [Databricks REST API 2.0](https://docs.databricks.com/dev-tools/api/latest/index.html)
- [Azure Databricks REST API 2.0](
    https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/)

The following articles provide information on the supported spec fields for the supported Databricks
Ops:  
- Cluster Ops: [Azure Databricks Cluster API](
    https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/clusters)
- Job Ops: [Azure Databricks Jobs API](
    https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/jobs)
- Run Ops: [Azure Databricks Jobs API - Runs Submit](
    https://docs.microsoft.com/en-us/azure/databricks/dev-tools/api/latest/jobs#--runs-submit)
