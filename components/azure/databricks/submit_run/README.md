# Sample Kubeflow pipeline with sample reusable component
Based on samples from:
- [Introduction to the Pipelines SDK](https://www.kubeflow.org/docs/pipelines/sdk/sdk-overview/)
- [Create Reusable Components](https://www.kubeflow.org/docs/pipelines/sdk/component-development/)
- [Build Lightweight Python Components](https://www.kubeflow.org/docs/pipelines/sdk/lightweight-python-components/)

Requirements:
- [Install the Kubeflow Pipelines SDK](https://www.kubeflow.org/docs/pipelines/sdk/install-sdk/)

## Test

1) Test program locally
    ```
    python ./src/program.py
    ```
2) Build component image
    ```
    bash build_image.sh
    ```
    It will output image name like alejacma/databricks_submit_run@sha256:ad87aedb2cd3b16505e25a326a0e9324cb34315c2f06064fab4958888ba313a1.
3) Use image name in component.yaml.
4) Build, upload and run pipeline:
    bash compile_upload_run.sh --kubeflow-host http://localhost:8080 --pipeline-name pipeline