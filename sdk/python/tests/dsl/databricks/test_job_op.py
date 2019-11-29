import unittest
import kfp
from kfp.dsl import PipelineParam
from kfp.dsl.databricks import CreateJobOp, DeleteJobOp

class TestCreateJobOp(unittest.TestCase):

    # TODO - test_databricks_create_job_without_k8s_or_run_name
    # TODO - test_databricks_create_job_with_new_cluster_and_spark_jar_task
    # TODO - test_databricks_create_job_with_new_cluster_and_spark_python_task
    # TODO - test_databricks_create_job_with_new_cluster_and_spark_submit_task
    # TODO - test_databricks_create_job_with_existing_cluster_and_notebook_task
    # TODO - test_databricks_create_job_with_spec_and_extra_args

    def test_databricks_create_job_with_spec(self):
        def my_pipeline():
            spec = {
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

            res = CreateJobOp(
                name="createjob",
                job_name="test-job",
                spec=spec
            )

            self.assertEqual(res.name, "createjob")
            self.assertEqual(res.resource.action, "create")
            self.assertEqual(
                res.resource.success_condition,
                "status.job_status.job_id > 0"
            )
            self.assertEqual(res.resource.failure_condition, None)
            self.assertEqual(res.resource.manifest, None)
            expected_attribute_outputs = {
                "name": "{.status.job_status.job_id}",
                "job_id": "{.status.job_status.job_id}",
                "job_name": "{.metadata.name}",
                "manifest": "{}"
            }
            self.assertEqual(res.attribute_outputs, expected_attribute_outputs)
            expected_outputs = {
                "name": PipelineParam(name="name", op_name=res.name),
                "job_id": PipelineParam(name="job_id", op_name=res.name),
                "job_name": PipelineParam(name="job_name", op_name=res.name),
                "manifest": PipelineParam(name="manifest", op_name=res.name)
            }
            self.assertEqual(res.outputs, expected_outputs)
            self.assertEqual(
                res.output,
                PipelineParam(name="name", op_name=res.name)
            )
            self.assertEqual(res.dependent_names, [])
            self.assertEqual(res.k8s_resource["kind"], "Djob")
            self.assertEqual(res.k8s_resource["metadata"]["name"], "test-job")
            self.assertEqual(res.k8s_resource["spec"], spec)

        kfp.compiler.Compiler()._compile(my_pipeline)

class TestDeleteJobOp(unittest.TestCase):

    def test_databricks_delete_job(self):
        def my_pipeline():

            res = DeleteJobOp(
                name="deletejob",
                job_name="test-job"
            )

            self.assertEqual(res.name, "deletejob")
            self.assertEqual(res.resource.action, "delete")
            self.assertEqual(res.resource.success_condition, None)
            self.assertEqual(res.resource.failure_condition, None)
            self.assertEqual(res.resource.manifest, None)
            self.assertEqual(res.attribute_outputs, {})
            self.assertEqual(res.outputs, {})
            self.assertEqual(res.output, None)
            self.assertEqual(res.dependent_names, [])
            self.assertEqual(res.k8s_resource["kind"], "Djob")
            self.assertEqual(res.k8s_resource["metadata"]["name"], "test-job")

        kfp.compiler.Compiler()._compile(my_pipeline)

if __name__ == '__main__':
    unittest.main()
