"""Create a new secret scope in Databricks."""
import kfp.dsl as dsl
import kfp.compiler as compiler

# https://docs.databricks.com/dev-tools/api/latest/secrets.html

@dsl.pipeline(
    name="DatabricksSecretScope",
    description="A toy pipeline that computes an approximation to pi with Databricks."
)
def calc_pipeline(
        scope_name="test-secretscope",
        string_secret="helloworld",
        byte_secret="aGVsbG93b3JsZA==",
        ref_secret_name="mysecret",
        ref_secret_key="username",
        principal_name="alejacma@microsoft.com"
    ):
    create_secret_task = dsl.ResourceOp(
        name="createsecret",
        k8s_resource={
            "apiVersion": "databricks.microsoft.com/v1alpha1",
            "kind": "SecretScope",
            "metadata": {
                "name": scope_name
            },
            "spec": {
                # initial_manage_permission as shown in operator's api\v1alpha1 or 
                # initial_manage_principal as in operator's config/samples/yaml/databricks_v1alpha1_secretscope.yaml?
                "initial_manage_permission": "users",
                "secrets": [
                    {
                        "key": "string-secret",
                        "string_value": string_secret
                    },
                    {
                        "key": "byte-secret",
                        "byte_value": byte_secret
                    },
                    {
                        "key": "ref-secret",
                        "value_from": {
                            "secret_key_ref": {
                                "name": ref_secret_name,
                                "key": ref_secret_key
                            }
                        }
                    }
                ],
                "acls": [
                    {
                        "principal": principal_name,
                        "permission": "READ"
                    }
                ]
            }
        },
        action="create",
        success_condition="status.secretscope.name !=",
        attribute_outputs={
            "name": "{.metadata.name}",
            "secretscope_name": "{.status.secretscope.name}",
            "backend_type": "{.status.secretscope.backend_type}"
        }
    )

    delete_secret_task = dsl.ResourceOp(
        name="deletesecret",
        k8s_resource={
            "apiVersion": "databricks.microsoft.com/v1alpha1",
            "kind": "SecretScope",
            "metadata": {
                "name": scope_name
            }
        },
        action="delete"
    )
    delete_secret_task.after(create_secret_task)

if __name__ == "__main__":
    compiler.Compiler().compile(calc_pipeline, __file__ + ".tar.gz")