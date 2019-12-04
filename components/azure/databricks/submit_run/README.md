# Sample Kubeflow pipeline with sample reusable component
Based on samples from:
- [Introduction to the Pipelines SDK](https://www.kubeflow.org/docs/pipelines/sdk/sdk-overview/)
- [Create Reusable Components](https://www.kubeflow.org/docs/pipelines/sdk/component-development/)
- [Build Lightweight Python Components](https://www.kubeflow.org/docs/pipelines/sdk/lightweight-python-components/)

Requirements:
- [Install the Kubeflow Pipelines SDK](https://www.kubeflow.org/docs/pipelines/sdk/install-sdk/)

## Test

1) Build component image
    ```
    bash build_image.sh
    ```
    This will update the image name in component.yaml.
2) Build, upload and run pipeline:
    bash compile_upload_run.sh --kubeflow-host http://localhost:8080 --pipeline-name pipeline