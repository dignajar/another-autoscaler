# Another Autoscaler
Another Autoscaler is a Kubernetes controller that automatically starts, stops, or restarts pods from a deployment at a specified time using a cron syntax.

Another Autoscaler read the annotation of each deployment and performs an increase or decrease in the number of replicas.

[![Docker image](https://img.shields.io/badge/Docker-image-blue.svg)](https://github.com/dignajar/another-autoscaler/pkgs/container/another-autoscaler)
[![Kubernetes YAML manifests](https://img.shields.io/badge/Kubernetes-manifests-blue.svg)](https://github.com/dignajar/another-autoscaler/tree/master/kubernetes)
[![codebeat badge](https://codebeat.co/badges/f57de995-ca62-49e5-b309-82ed60570324)](https://codebeat.co/projects/github-com-dignajar-another-autoscaler-master)
[![release](https://img.shields.io/github/v/release/dignajar/another-autoscaler.svg)](https://github.com/dignajar/another-autoscaler/releases)
[![license](https://img.shields.io/badge/license-MIT-green)](https://github.com/dignajar/another-autoscaler/blob/master/LICENSE)

> The date and time must be in UTC.

> The restart feature execute a rollout restart deployment.

## Use cases
- Cost savings by reducing the number of replicas after working hours or weekends.
- Stop GPU deployments during non-working hours.

Another Autoscaler is a perfect combination with [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler).

## Installation
```
# Deploy Another Autoscaler into Kubernetes on "another" namespace
kubectl apply -f https://raw.githubusercontent.com/dignajar/another-autoscaler/master/kubernetes/full.yaml

# Check if Another Autoscaler is working
kubectl get pods -n another
```

## Configuration
The following annotations for the deployments are valid (`metadata.annotations`).

- `another-autoscaler/stop-time`: Define the date and time when the replica of the deployment will be set to 0.
- `another-autoscaler/start-time` Define the date and time when the replica of the deployment will be set to 1.
- `another-autoscaler/restart-time:`: Define the date and time when the rollout restart will be peformerd to a deployment.
- `another-autoscaler/stop-replicas`: This is the number of replicas to set when Another Autoscaler scale down the deployment, by default is 0.
- `another-autoscaler/start-replicas`: This is the number of replicas to set when Another Autoscaler scale up the deployment, by default is 1.

## Examples

### Stop pods at 6pm every day:
```
another-autoscaler/stop-time: "00 18 * * *"
```

### Start pods at 1pm every day:
```
another-autoscaler/start-time: "00 13 * * *"
```

### Start 3 pods at 2:30pm every day:
```
another-autoscaler/start-time: "30 14 * * *"
another-autoscaler/start-replicas: "3"
```

### Restart pods at 9:15am every day:
```
another-autoscaler/restart-time: "15 09 * * *"
```

### Restart pods at 2:30am, only on Saturday and Sunday:
```
another-autoscaler/restart-time: "00 02 * * 0,6"
```

### Full example, how to start pods at 2pm and stop them at 3pm every day
The following example start `5` replicas in total at `2pm` and stop `4` of them at `3pm` every day, the deployment start with `0` replicas.

The `start-replicas` is not incremental, the value is the number of replicas will be setup by Another Autoscaler at the defined time by `start-time`.

> The date and time must be in UTC.

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
  annotations:
    another-autoscaler/start-time: "00 14 * * *"
    another-autoscaler/start-replicas: "5"
    another-autoscaler/stop-time: "00 15 * * *"
    another-autoscaler/stop-replicas: "1"
spec:
  replicas: 0
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```

## GitOps / FluxCD
To avoid conflicts with Flux and Another Autoscaler, you can remove the field `spec.replicas` from your deployment manifest and leave Another Autoscaler to manage the number of replicas.

## Docker and Minikube development environment

This step allows developer to create a kubernetes environment.

Requirements: [Minikube](https://minikube.sigs.k8s.io/docs/) and [Docker](https://docs.docker.com/engine/)

```
minikube start
minikube addons enable registry
docker build -t localhost:49155/another-autoscaler:latest .
docker push localhost:49155/another-autoscaler:latest

```

To discard environment
```
minikube stop
minikube delete
```