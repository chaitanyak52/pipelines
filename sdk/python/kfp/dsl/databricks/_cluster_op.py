from .._resource_op import ResourceOp

class CreateClusterOp(ResourceOp):
    """Represents an op which will be translated into a Databricks Cluster creation resource
    template.

    Example:

        import kfp.dsl.databricks as databricks

        databricks.CreateClusterOp(
            name="createcluster",
            cluster_name="test-cluster",
            spec={
                "spark_version":"5.3.x-scala2.11",
                "node_type_id": "Standard_D3_v2",
                "spark_conf": {
                    "spark.speculation": "true"
                },
                "num_workers": 2
            }
        )
    """

    def __init__(self,
                 name: str = None,
                 cluster_name: str = None,
                 spec=None):
        """Create a new instance of CreateClusterOp.

        Args:

            name: the name of the op. It does not have to be unique within a pipeline
                because the pipeline will generate a new unique name in case of a conflict.
            cluster_name: the name of the Databricks cluster.
            spec: Specification of the Databricks cluster to create.

        Raises:

            ValueError: if not inside a pipeline
                        if the name is an invalid string
                        if no cluster name is provided
        """

        if not cluster_name:
            raise ValueError("You need to provide a cluster_name.")

        if not spec:
            raise ValueError("You need to provide a spec.")

        super().__init__(
            k8s_resource={
                "apiVersion": "databricks.microsoft.com/v1alpha1",
                "kind": "Dcluster",
                "metadata": {
                    "name": cluster_name,
                },
                "spec": spec,
            },
            action="create",
            success_condition="status.cluster_info.cluster_id != ",
            attribute_outputs={
                "name": "{.status.cluster_info.cluster_id}",
                "cluster_id": "{.status.cluster_info.cluster_id}",
                "cluster_name": "{.metadata.name}"
            },
            name=name)

    @property
    def resource(self):
        """`Resource` object that represents the `resource` property in
        `io.argoproj.workflow.v1alpha1.Template`.
        """
        return self._resource

class DeleteClusterOp(ResourceOp):
    """Represents an op which will be translated into a Databricks Cluster deletion resource
    template.

    Example:

        import kfp.dsl.databricks as databricks

        databricks.DeleteClusterOp(
            name="deletecluster",
            cluster_name="test-cluster"
        )
    """

    def __init__(self,
                 name: str = None,
                 cluster_name: str = None):
        """Create a new instance of DeleteClusterOp.

        Args:

            name: the name of the op. It does not have to be unique within a pipeline
                because the pipeline will generate a new unique name in case of a conflict.
            cluster_name: the name of the Databricks cluster.

        Raises:

            ValueError: if not inside a pipeline
                        if the name is an invalid string
                        if no cluster name is provided
        """

        if not cluster_name:
            raise ValueError("You need to provide a cluster_name.")

        super().__init__(
            k8s_resource={
                "apiVersion": "databricks.microsoft.com/v1alpha1",
                "kind": "Dcluster",
                "metadata": {
                    "name": cluster_name,
                },
            },
            action="delete",
            name=name)

    @property
    def resource(self):
        """`Resource` object that represents the `resource` property in
        `io.argoproj.workflow.v1alpha1.Template`.
        """
        return self._resource
