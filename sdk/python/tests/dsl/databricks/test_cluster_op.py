import kfp
from kfp.dsl import PipelineParam
from kfp.dsl.databricks import CreateClusterOp, DeleteClusterOp
import unittest

class TestCreateClusterOp(unittest.TestCase):

    def test_databricks_create_cluster(self):
        def my_pipeline():

            spec = {
                "spark_version":"5.3.x-scala2.11",
                "node_type_id": "Standard_D3_v2",
                "spark_conf": {
                    "spark.speculation": "true"
                },
                "num_workers": 2
            }

            res = CreateClusterOp(
                name="createcluster",
                cluster_name="test-cluster",
                spec=spec
            )

            self.assertEqual(res.name, "createcluster")
            self.assertEqual(res.resource.action, "create")
            self.assertEqual(
                res.resource.success_condition,
                "status.cluster_info.cluster_id != "
            )
            self.assertEqual(res.resource.failure_condition, None)
            self.assertEqual(res.resource.manifest, None)
            expected_attribute_outputs = {
                "name": "{.status.cluster_info.cluster_id}",
                "cluster_id": "{.status.cluster_info.cluster_id}",
                "cluster_name": "{.metadata.name}",
                "manifest": "{}"
            }
            self.assertEqual(res.attribute_outputs, expected_attribute_outputs)
            expected_outputs = {
                "name": PipelineParam(name="name", op_name=res.name),
                "cluster_id": PipelineParam(name="cluster_id", op_name=res.name),
                "cluster_name": PipelineParam(name="cluster_name", op_name=res.name),
                "manifest": PipelineParam(name="manifest", op_name=res.name)
            }
            self.assertEqual(res.outputs, expected_outputs)
            self.assertEqual(
                res.output,
                PipelineParam(name="name", op_name=res.name)
            )
            self.assertEqual(res.dependent_names, [])    
            self.assertEqual(res.k8s_resource["kind"], "Dcluster")
            self.assertEqual(res.k8s_resource["metadata"]["name"], "test-cluster")
            self.assertEqual(res.k8s_resource["spec"], spec)

        kfp.compiler.Compiler()._compile(my_pipeline)


class TestDeleteClusterOp(unittest.TestCase):

    def test_databricks_delete_cluster(self):
        def my_pipeline():

            res = DeleteClusterOp(
                name = "deletecluster",
                cluster_name = "test-cluster"
            )

            self.assertEqual(res.name, "deletecluster")
            self.assertEqual(res.resource.action, "delete")
            self.assertEqual(res.resource.success_condition, None)
            self.assertEqual(res.resource.failure_condition, None)
            self.assertEqual(res.resource.manifest, None)
            self.assertEqual(res.attribute_outputs, {})
            self.assertEqual(res.outputs, {})
            self.assertEqual(res.output, None)
            self.assertEqual(res.dependent_names, [])    
            self.assertEqual(res.k8s_resource["kind"], "Dcluster")
            self.assertEqual(res.k8s_resource["metadata"]["name"], "test-cluster")

        kfp.compiler.Compiler()._compile(my_pipeline)

if __name__ == '__main__':
    unittest.main()