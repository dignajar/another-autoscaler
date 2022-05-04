from datetime import datetime, timezone, timedelta
from croniter import croniter
from dateutil import parser
from k8s import K8s
from logs import Logs


class Deployments:

    def __init__(self):
        self.logs = Logs(self.__class__.__name__)
        self.k8s = K8s.getInstance()

    def __start__(self, namespace: str, deploy: dict, currentTime: datetime):
        '''
            Logic for start the pods
        '''
        deployName = deploy.metadata.name
        deployAnnotations = deploy.metadata.annotations
        deployReplicas = deploy.spec.replicas

        startAnnotation = 'another-autoscaler/start-time'
        if startAnnotation not in deployAnnotations:
            return

        self.logs.debug({'message': 'Start time detected.',
                        'namespace': namespace, 'deployment': deployName})
        startTime = deployAnnotations[startAnnotation]

        try:
            if not croniter.match(startTime, currentTime):
                return
        except:
            self.logs.error(
                {'message': 'Error in start-time annotation', 'namespace': namespace, 'deployment': deployName})
            return

        self.logs.debug({'message': 'Start time Cron expression matched.', 'namespace': namespace,
                        'deployment': deployName, 'startTime': str(startTime), 'currentTime': str(currentTime)})

        # start-replicas
        startReplicas = 1
        startReplicasAnnotation = 'another-autoscaler/start-replicas'
        if startReplicasAnnotation not in deployAnnotations:
            return

        self.logs.debug({'message': 'Number of replicas.', 'namespace': namespace,
                        'deployment': deployName, 'startReplicas': deployAnnotations[startReplicasAnnotation]})
        try:
            startReplicas = int(
                deployAnnotations[startReplicasAnnotation])
        except:
            startReplicas = 1

        if deployReplicas == startReplicas:
            return

        self.logs.info({'message': 'Deployment set to start.', 'namespace': namespace, 'deployment': deployName,
                        'startTime': str(startTime),
                        'availableReplicas': deploy.status.available_replicas,
                        'startReplicas': str(startReplicas)})
        self.k8s.setReplicas(namespace, deployName, startReplicas)

    def __stop__(self, namespace: str, deploy: dict, currentTime: datetime):
        '''
            Logic for stop the pods
        '''
        deployName = deploy.metadata.name
        deployAnnotations = deploy.metadata.annotations
        deployReplicas = deploy.spec.replicas

        stopAnnotation = 'another-autoscaler/stop-time'
        if stopAnnotation not in deployAnnotations:
            return

        self.logs.debug({'message': 'Stop time detected.',
                        'namespace': namespace, 'deployment': deployName})
        stopTime = deployAnnotations[stopAnnotation]

        try:
            if not croniter.match(stopTime, currentTime):
                return
        except:
            self.logs.error(
                {'message': 'Error in stop-time annotation', 'namespace': namespace, 'deployment': deployName})
            return

        self.logs.debug({'message': 'Stop time Cron expression matched.', 'namespace': namespace,
                        'deployment': deployName, 'stopTime': str(stopTime), 'currentTime': str(currentTime)})

        # stop-replicas
        stopReplicas = 0
        stopReplicasAnnotation = 'another-autoscaler/stop-replicas'
        if stopReplicasAnnotation not in deployAnnotations:
            return

        self.logs.debug({'message': 'Number of replicas.', 'namespace': namespace,
                        'deployment': deployName, 'stopReplicas': deployAnnotations[stopReplicasAnnotation]})

        try:
            stopReplicas = int(
                deployAnnotations[stopReplicasAnnotation])
        except:
            stopReplicas = 0

        if deployReplicas == stopReplicas:
            return

        self.logs.info({'message': 'Deployment set to stop.', 'namespace': namespace, 'deployment': deployName,
                        'stopTime': str(stopTime),
                        'availableReplicas': deploy.status.available_replicas,
                        'stopReplicas': str(stopReplicas)})
        self.k8s.setReplicas(namespace, deployName, stopReplicas)

    def __restart__(self, namespace: str, deploy: dict, currentTime: datetime):
        '''
            Logic for restart the pods
        '''
        deployName = deploy.metadata.name
        deployAnnotations = deploy.metadata.annotations

        restartAnnotation = 'another-autoscaler/restart-time'
        if restartAnnotation not in deployAnnotations:
            return

        self.logs.debug({'message': 'Restart time detected.',
                        'namespace': namespace, 'deployment': deployName})
        restartTime = deployAnnotations[restartAnnotation]

        try:

            if not croniter.match(restartTime, currentTime):
                return
        except:
            self.logs.error(
                {'message': 'Error in restart-time annotation', 'namespace': namespace, 'deployment': deployName})
            return

        self.logs.debug({'message': 'Restart time Cron expression matched.', 'namespace': namespace,
                        'deployment': deployName, 'restartTime': str(restartTime), 'currentTime': str(currentTime)})

        # Check if was already restarted
        try:
            restartedAt = parser.parse(
                deploy.spec.template.metadata.annotations['kubectl.kubernetes.io/restartedAt'])
        except:
            restartedAt = currentTime - timedelta(days=1)

        if ((currentTime - restartedAt).total_seconds() / 60.0) <= 1:
            return

        self.logs.info({'message': 'Deployment set to restart.', 'namespace': namespace,
                        'deployment': deployName, 'restartTime': str(restartTime), 'currentTime': str(currentTime)})
        self.k8s.rolloutDeployment(namespace, deployName)
