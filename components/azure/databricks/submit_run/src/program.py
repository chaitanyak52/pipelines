#!/usr/bin/env python3
import argparse
from pprint import pprint
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Function doing the actual work (Outputs first N lines from a text file)
def do_work():

    run_name = "test-run"
    parameter = "10"
    api = client.CustomObjectsApi()

    try:
        api_response = api.create_namespaced_custom_object(
            group="databricks.microsoft.com",
            version="v1alpha1",
            namespace="kubeflow",
            plural="runs",
            body={
                "apiVersion": "databricks.microsoft.com/v1alpha1",
                "kind": "Run",
                "metadata": {"name": run_name},
                "spec": {
                    "new_cluster": {
                        "spark_version": "5.3.x-scala2.11",
                        "node_type_id": "Standard_D3_v2",
                        "num_workers": 10,
                    },
                    "libraries": [
                        {
                            "jar": "dbfs:/my-jar.jar",
                            "maven": {"coordinates": "org.jsoup:jsoup:1.7.2"},
                        }
                    ],
                    "spark_jar_task": {"main_class_name": "com.databricks.ComputeModels"},
                },
            },
            pretty="true"
        )
        pprint(api_response)
    except ApiException as ex:
        print("Exception when calling ApiextensionsV1beta1Api->create_custom_resource_definition: %s\n" % ex)  

# Defining and parsing the command-line arguments
parser = argparse.ArgumentParser(description='My program description')
parser.add_argument('--input1-path', type=str, help='Path of the local file containing the Input 1 data.') # Paths should be passed in, not hardcoded
parser.add_argument('--param1', type=int, default=100, help='Parameter 1.')
parser.add_argument('--output1-path', type=str, help='Path of the local file where the Output 1 data should be written.') # Paths should be passed in, not hardcoded
args = parser.parse_args()

print("loading config")
#config.load_kube_config()
config.load_incluster_config()
print("doing work")
do_work()
print("done")