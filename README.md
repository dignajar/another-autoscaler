# Another Scheduler
Automatically Start and Stop pods from a deployment at a specific time by cron annotation.

Another Scheduler checks the annotation for each deployment and performs an scale up or scale down of the number replicas.

> The date and time must be in UTC.
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
another-scheduler.io/start-replicas: "3"
```
## Example: How to start pods at 2pm and stop them at 3pm every day
The following example start `5` replicas in total at `2pm` and stop `4` of them at `3pm` every day, the deployment start with `0` replicas.

The `start-replicas` is not incremental, the value is the number of replicas will be setup by Another Scheduler at the time defined by `start-time`.

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