"""Import an item into a Databricks Workspace."""
import kfp.dsl as dsl
import kfp.compiler as compiler

# https://docs.databricks.com/dev-tools/api/latest/workspace.html#import
# path	STRING	The absolute path of the notebook or directory. Importing directory is only support for DBC format. This field is required.
# format	ExportFormat	This specifies the format of the file to be imported. By default, this is SOURCE. However it may be one of: SOURCE, HTML, JUPYTER, DBC. The value is case sensitive.
# language	Language	The language. If format is set to SOURCE, this field is required; otherwise, it will be ignored.
# content	BYTES	The base64-encoded content. This has a limit of 10 MB. If the limit (10MB) is exceeded, exception with error code MAX_NOTEBOOK_SIZE_EXCEEDED will be thrown. This parameter might be absent, and instead a posted file will be used. See Import a notebook or directory for more information about how to use it.
# overwrite	BOOL	The flag that specifies whether to overwrite existing object. It is false by default. For DBC format, overwrite is not supported since it may contain a directory.
def import_workspace_item(item_name):
    return dsl.ResourceOp(
        name="importworkspaceitem",
        k8s_resource={
            "apiVersion": "databricks.microsoft.com/v1alpha1",
            "kind": "WorkspaceItem",
            "metadata": {
                "name": item_name
            },
            "spec":{
                "content": "MSsx",
                "path": "/Users/alejacma@microsoft.com/ScalaExampleNotebook",
                "language": "SCALA",
                "overwrite": True,
                "format": "SOURCE"
            }
        },
        action="create",
        success_condition="status.object_hash",
        attribute_outputs={
            "name": "{.metadata.name}",
            "object_hash": "{.status.object_hash}",
            "object_language": "{.status.object_info.language}",
            "object_type": "{.status.object_info.object_type}",
            "object_path": "{.status.object_info.path}"
        }
    )

def delete_workspace_item(item_name):
    return dsl.ResourceOp(
        name="deleteworkspaceitem",
        k8s_resource={
            "apiVersion": "databricks.microsoft.com/v1alpha1",
            "kind": "WorkspaceItem",
            "metadata": {
                "name": item_name,
            }
        },
        action="delete"
    )

@dsl.pipeline(
    name="DatabricksWorkspaceItem",
    description="A toy pipeline that imports some source code into a Databricks Workspace."
)
def calc_pipeline(item_name="test-item"):
    import_workspace_item_task = import_workspace_item(item_name)
    delete_workspace_item_task = delete_workspace_item(item_name)
    delete_workspace_item_task.after(import_workspace_item_task)

if __name__ == "__main__":
    compiler.Compiler().compile(calc_pipeline, __file__ + ".tar.gz")
