"""
Free Tier Flask API service.

This module provides a minimal Flask application that exposes an endpoint to launch
Kubernetes jobs in the 'free-service' namespace.

Students should extend this code to add additional endpoints, error handling,
or business logic as required by the assignment.
"""

from kubernetes import client, config, utils
from flask import Flask, request
import yaml
import time

# Load Kubernetes configuration 
try:
    config.load_incluster_config() # when it's in cluster, it doesn't need kube config
except config.config_exception.ConfigException:
    config.load_kube_config()  # running it without a cluster

# Initialize Flask app
v1 = client.CoreV1Api()
app = Flask(__name__)

# TODO: Define a POST endpoint that:
#   - Parses the incoming JSON for the 'dataset' parameter
#   - Loads the job YAML template
#   - Injects the dataset value into the job spec
#   - Generates a unique job name
#   - Submits the job to the Kubernetes cluster
#   - Returns a success or error response
@app.route('/free', methods=['POST'])       # TODO: how do I determine the path? is it just /free?
def post_free():
    namespace = "free-service"
    uniqueName = "free-service-job-" + str(time.time())
    dataSet = request.get_json()['dataset']    # this is just a string for kmnist or mnist

    with open('/app/free-tier-job.yaml', 'r') as f:
        jobSpec = yaml.load(f, Loader=yaml.Loader)

    jobSpec['metadata']['name'] = uniqueName
    jobSpec['spec']['template']['metadata']['labels']['dataset'] = dataSet # TODO
    with open('/app/free-tier-job.yaml', 'w') as file:
        yaml.dump(jobSpec, file)

    try:
        response = v1.create_namespaced_job(
            body=jobSpec,
            namespace=namespace
        )
        return f"Job created: {response.metadata.name}", 200
    except ApiException as e:
        return f"Exception when calling BatchV1Api->create_namespaced_job: {e}", 500
        
'''
use kubernetes api to check if successfully launched
and then log into the instance to check if everything is working

docker run -it \ -v ~/.kube/config:/root/.kube/config \ free-tier-app:v1
'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)