# Sample Kubeflow pipeline with sample reusable component
Based on samples from:
- [Introduction to the Pipelines SDK](https://www.kubeflow.org/docs/pipelines/sdk/sdk-overview/)
- [Create Reusable Components](https://www.kubeflow.org/docs/pipelines/sdk/component-development/)

## Requirements:
1) [Create an Azure Databricks workspace](
    https://docs.microsoft.com/en-us/azure/databricks/getting-started/try-databricks?toc=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Fazure-databricks%2FTOC.json&bc=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Fbread%2Ftoc.json#--step-2-create-an-azure-databricks-workspace)
2) [Deploy the Azure Databricks Operator for Kubernetes](
    https://github.com/microsoft/azure-databricks-operator/blob/master/docs/deploy.md)
3) [Install the Kubeflow Pipelines SDK](https://www.kubeflow.org/docs/pipelines/sdk/install-sdk/)

## How to test

1) Build component image
    ```
    bash build_image.sh
    ```
    This will update the image name in component.yaml.
2) Build, upload and run pipeline:
    bash compile_upload_run.sh --kubeflow-host http://localhost:8080 --pipeline-name pipeline