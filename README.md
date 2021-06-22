# Another Scheduler
Automatically Start and Stop pods from a deployment at a specific time by cron annotation.

Another Scheduler checks the annotation for each deployment and performs an scale up or scale down of the number replicas.

## Annotations
Stop pods at 2pm every day:
```
another-scheduler.io/stop-time: "00 14 * * *"
```

Start pods at 3pm every day:
```
another-scheduler.io/start-time: "00 15 * * *"
```

Start 3 pods at 6pm every day:
```
another-scheduler.io/start-time: "00 18 * * *"
another-scheduler.io/replicas: "3"
```
## How to start pods at 2pm and stop them at 3pm every day
The following example start `5` replicas at `2pm` and stop them at `3pm` every day.

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
  annotations:
    another-scheduler.io/start-time: "00 14 * * *"
    another-scheduler.io/stop-time: "00 15 * * *"
    another-scheduler.io/replicas: "5"
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