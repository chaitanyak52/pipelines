#!/usr/bin/env python3
import logging
import argparse
import json
from kubernetes import client, config
from kubernetes.client.rest import ApiException

def parse_args():
    logging.info("Parsing args...")
    parser = argparse.ArgumentParser()
    parser.add_argument('--run_name', type=str)
    parser.add_argument('--new_cluster', type=json.loads)
    parser.add_argument('--libraries', type=json.loads)
    parser.add_argument('--spark_jar_task', type=json.loads)
    args = parser.parse_args()
    logging.debug(args)
    return args

def create_namespaced_custom_object_spec(args):
    logging.info("Preparing custom object spec...")
    spec = {}
    spec["run_name"] = args.run_name
    spec["new_cluster"] = args.new_cluster
    spec["libraries"] = args.libraries
    spec["spark_jar_task"] = args.spark_jar_task
    logging.debug(spec)
    return spec

def create_namespaced_custom_object(k8s_name, spec):

    logging.info("Loading in-cluster config...")
    config.load_incluster_config()
    api = client.CustomObjectsApi()

    try:
        logging.info("Creating custom object...")
        api_response = api.create_namespaced_custom_object(
            group="databricks.microsoft.com",
            version="v1alpha1",
            namespace="kubeflow", # TODO - Accept namespace as a parameter
            plural="runs",
            body={
                "apiVersion": "databricks.microsoft.com/v1alpha1",
                "kind": "Run",
                "metadata": {"name": k8s_name},
                "spec": spec,
            },
            pretty="true"
        )
        logging.debug(api_response)

        logging.info("Writing output...")
        with open("run_id", 'w') as run_id:
            run_id.write("test")

        logging.info("Work done!")

    except ApiException as ex:
        logging.error("Exception when calling CustomObjectsApi->create_namespaced_custom_object: %s\n", ex)

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

ARGS = parse_args()
SPEC = create_namespaced_custom_object_spec(ARGS)
create_namespaced_custom_object(ARGS.run_name, SPEC)
