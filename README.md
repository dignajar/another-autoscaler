# Another Scheduler
Another Scheduler is a Kubernetes controller that automatically starts, stops, or restarts pods from a deployment at a specified time using a cron syntax.

Another Scheduler read the annotation of each deployment and performs an increase or decrease in the number of replicas.

> The date and time must be in UTC.

> The restart feature execute a rollout restart deployment.

---
[![Docker image](https://img.shields.io/badge/Docker-image-blue.svg)](https://hub.docker.com/r/dignajar/another-scheduler)
[![Kubernetes YAML manifests](https://img.shields.io/badge/Kubernetes-manifests-blue.svg)](https://github.com/dignajar/another-scheduler/tree/master/kubernetes)
[![codebeat badge](https://codebeat.co/badges/f57de995-ca62-49e5-b309-82ed60570324)](https://codebeat.co/projects/github-com-dignajar-another-scheduler-master)
[![release](https://img.shields.io/github/v/release/dignajar/another-scheduler.svg)](https://github.com/dignajar/another-scheduler/releases)
[![license](https://img.shields.io/badge/license-MIT-green)](https://github.com/dignajar/another-scheduler/blob/master/LICENSE)
---

## Annotations
Stop pods at 6pm every day:
```
another-scheduler.io/stop-time: "00 18 * * *"
```

Start pods at 1pm every day:
```
another-scheduler.io/start-time: "00 13 * * *"
```

Start 3 pods at 2:30pm every day:
```
another-scheduler.io/start-time: "30 14 * * *"
another-scheduler.io/start-replicas: "3"
```

Restart pods at 9:15am every day:
```
another-scheduler.io/restart-time: "15 09 * * *"
```

Restart pods at 2:30am, only on Saturday and Sunday:
```
another-scheduler.io/restart-time: "00 02 * * 0,6"
```

## Example: How to start pods at 2pm and stop them at 3pm every day
The following example start `5` replicas in total at `2pm` and stop `4` of them at `3pm` every day, the deployment start with `0` replicas.

The `start-replicas` is not incremental, the value is the number of replicas will be setup by Another Scheduler at the defined time by `start-time`.

> The date and time must be in UTC.

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
  annotations:
    another-scheduler.io/start-time: "00 14 * * *"
    another-scheduler.io/start-replicas: "5"
    another-scheduler.io/stop-time: "00 15 * * *"
    another-scheduler.io/stop-replicas: "1"
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

## Deploy Another Scheduler into Kubernetes
```
kubectl apply -f https://raw.githubusercontent.com/dignajar/another-scheduler/master/kubernetes/full.yaml
```
