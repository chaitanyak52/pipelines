from .._resource_op import ResourceOp

# Azure Databricks Operator and Golang SDK for Databricks types:
#   Djob: [type Djob struct](https://github.com/microsoft/azure-databricks-operator/blob/master/api/v1alpha1/djob_types.go)
#       spec: [type JobSettings struct](https://github.com/xinsnake/databricks-sdk-golang/blob/master/azure/models/JobSettings.go)
#       status.job_status: [type Job struct](https://github.com/xinsnake/databricks-sdk-golang/blob/master/azure/models/Job.go)
#       status.last_10_runs: [type Run struct](https://github.com/xinsnake/databricks-sdk-golang/blob/master/azure/models/Run.go)
# Databricks Rest API 2.0 Data Structures:
#   [Jobs API Data Structures](https://docs.databricks.com/dev-tools/api/latest/jobs.html#data-structures) 
#   [Clusters API Data Structures](https://docs.databricks.com/dev-tools/api/latest/clusters.html#data-structures)

class CreateJobOp(ResourceOp):
    """Represents an op which will be translated into an Azure Databricks Spark Job creation resource template.

    Example:

        import kfp.dsl.databricks as databricks

        databricks.CreateJobOp(
            name="createjob",
            job_name="test-job",
            spec={
                "new_cluster" : {
                    "spark_version":"5.3.x-scala2.11",
                    "node_type_id": "Standard_D3_v2",
                    "num_workers": 2
                },
                "libraries" : [
                    {
                        "jar": 'dbfs:/my-jar.jar'
                    },
                    {
                        "maven": {
                            "coordinates": 'org.jsoup:jsoup:1.7.2'
                        }
                    }
                ],
                "timeout_seconds" : 3600,
                "max_retries": 1,
                "schedule":{
                    "quartz_cron_expression": "0 15 22 ? * *",
                    "timezone_id": "America/Los_Angeles",
                },
                "spark_jar_task": {
                    "main_class_name": "com.databricks.ComputeModels",
                },
            }
        )
    """

    def __init__(self,
        name: str = None,
        job_name: str = None,
        spec=None):
        """Create a new instance of CreateJobOp.

        Args:

            name: the name of the op. It does not have to be unique within a pipeline
                because the pipeline will generates a unique new name in case of conflicts.
            job_name: the name of the Spark Job.
            spec: Specification of the Spark job to create.

        Raises:
            ValueError: if not inside a pipeline
                        if the name is an invalid string
                        if no job name is provided
                        if no spec is provided
        """

        if not job_name:
            raise ValueError("You need to provide a job_name.")

        if not spec:
            raise ValueError("You need to provide a spec.")

        super().__init__(
            k8s_resource = {
                "apiVersion": "databricks.microsoft.com/v1alpha1",
                "kind": "Djob",
                "metadata": {
                    "name": job_name
                },
                "spec": spec
            }, 
            action = "create", 
            success_condition = "status.job_status.job_id > 0", 
            attribute_outputs = {
                "name": "{.status.job_status.job_id}",
                "job_id": "{.status.job_status.job_id}",
                "job_name": "{.metadata.name}"
            },
            name = name)

    @property
    def resource(self):
        """`Resource` object that represents the `resource` property in
        `io.argoproj.workflow.v1alpha1.Template`.
        """
        return self._resource

class DeleteJobOp(ResourceOp):
    """Represents an op which will be translated into an Azure Databricks Spark Job deletion resource template.

    Example:

        import kfp.dsl.databricks as databricks
        
        databricks.DeleteJobOp(
            name = "deletejob",
            job_name = create_job_result.outputs["job_name"]
        )
    """

    def __init__(self,
        name: str = None,
        job_name: str = None):
        """Create a new instance of DeleteJobOp.

        Args:

            name: the name of the op. It does not have to be unique within a pipeline
                because the pipeline will generates a unique new name in case of conflicts.
            job_name: the name of the Spark Job.

        Raises:

            ValueError: if not inside a pipeline
                        if the name is an invalid string
                        if no job name is provided
        """
        
        if not job_name:
            raise ValueError("You need to provide a job_name.")

        super().__init__(
            k8s_resource={
                "apiVersion": "databricks.microsoft.com/v1alpha1",
                "kind": "Djob",
                "metadata": {
                    "name": job_name,
            },
        }, 
        action="delete", 
        name = name)

    @property
    def resource(self):
        """`Resource` object that represents the `resource` property in
        `io.argoproj.workflow.v1alpha1.Template`.
        """
        return self._resource