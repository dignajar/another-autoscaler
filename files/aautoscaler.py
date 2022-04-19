import os
from croniter import croniter
from datetime import date, datetime, timezone, timedelta
from dateutil import parser
from logs import Logs
from k8s import K8s

class AAutoscaler:

    def __init__(self):
        self.logs = Logs(self.__class__.__name__)

        # K8s client object
        # Auth via Bearer token
        if 'K8S_BEARER_TOKEN' in os.environ and 'K8S_API_ENDPOINT' in os.environ:
            self.logs.info({'message': 'Kubernetes object via bearer token.'})
            k8sAPI = os.environ.get('K8S_API_ENDPOINT')
            k8sToken = os.environ.get('K8S_BEARER_TOKEN')
            self.k8s = K8s(k8sAPI, k8sToken)
        # Auth via in-cluster configuration, running inside a pod
        elif 'KUBERNETES_SERVICE_HOST' in os.environ:
            self.logs.info({'message': 'Kubernetes object via in-cluster configuration.'})
            self.k8s = K8s()
        else:
            self.logs.error({'message': 'Error trying to create the Kubernetes object.'})
            raise Exception('Error trying to create the Kubernetes object.')

    def __start__(self, namespace:str, deploy:dict, currentTime:datetime):
        '''
            Logic for start the pods
        '''
        deployName = deploy.metadata.name
        deployAnnotations = deploy.metadata.annotations
        deployReplicas = deploy.spec.replicas

        startAnnotation = 'another-autoscaler/start-time'
        if startAnnotation in deployAnnotations:
            self.logs.debug({'message': 'Start time detected.', 'namespace': namespace, 'deployment': deployName})
            startTime = deployAnnotations[startAnnotation]

            if croniter.match(startTime, currentTime):
                self.logs.debug({'message': 'Start time Cron expression matched.', 'namespace': namespace, 'deployment': deployName, 'startTime': str(startTime), 'currentTime': str(currentTime)})

                # start-replicas
                startReplicas = 1
                startReplicasAnnotation = 'another-autoscaler/start-replicas'
                if startReplicasAnnotation in deployAnnotations:
                    self.logs.debug({'message': 'Number of replicas.', 'namespace': namespace, 'deployment': deployName, 'startReplicas': deployAnnotations[startReplicasAnnotation]})
                    startReplicas = int(deployAnnotations[startReplicasAnnotation])

                if deployReplicas != startReplicas:
                    self.logs.info({'message': 'Deployment set to start.', 'namespace': namespace, 'deployment': deployName, 'startTime': str(startTime), 'availableReplicas': deploy.status.available_replicas, 'startReplicas': str(startReplicas)})
                    self.k8s.setReplicas(namespace, deployName, startReplicas)

    def __stop__(self, namespace:str, deploy:dict, currentTime:datetime):
        '''
            Logic for stop the pods
        '''
        deployName = deploy.metadata.name
        deployAnnotations = deploy.metadata.annotations
        deployReplicas = deploy.spec.replicas

        stopAnnotation = 'another-autoscaler/stop-time'
        if stopAnnotation in deployAnnotations:
            self.logs.debug({'message': 'Stop time detected.', 'namespace': namespace, 'deployment': deployName})
            stopTime = deployAnnotations[stopAnnotation]

            if croniter.match(stopTime, currentTime):
                self.logs.debug({'message': 'Stop time Cron expression matched.', 'namespace': namespace, 'deployment': deployName, 'stopTime': str(stopTime), 'currentTime': str(currentTime)})

                # stop-replicas
                stopReplicas = 0
                stopReplicasAnnotation = 'another-autoscaler/stop-replicas'
                if stopReplicasAnnotation in deployAnnotations:
                    self.logs.debug({'message': 'Number of replicas.', 'namespace': namespace, 'deployment': deployName, 'stopReplicas': deployAnnotations[stopReplicasAnnotation]})
                    stopReplicas = int(deployAnnotations[stopReplicasAnnotation])

                if deployReplicas != stopReplicas:
                    self.logs.info({'message': 'Deployment set to stop.', 'namespace': namespace, 'deployment': deployName, 'stopTime': str(stopTime), 'availableReplicas': deploy.status.available_replicas, 'stopReplicas': str(stopReplicas)})
                    self.k8s.setReplicas(namespace, deployName, stopReplicas)

    def __restart__(self, namespace:str, deploy:dict, currentTime:datetime):
        '''
            Logic for restart the pods
        '''
        deployName = deploy.metadata.name
        deployAnnotations = deploy.metadata.annotations

        restartAnnotation = 'another-autoscaler/restart-time'
        if restartAnnotation in deployAnnotations:
            self.logs.debug({'message': 'Restart time detected.', 'namespace': namespace, 'deployment': deployName})
            restartTime = deployAnnotations[restartAnnotation]

            if croniter.match(restartTime, currentTime):
                self.logs.debug({'message': 'Restart time Cron expression matched.', 'namespace': namespace, 'deployment': deployName, 'restartTime': str(restartTime), 'currentTime': str(currentTime)})

                # Check if was already restarted
                try:
                    restartedAt = parser.parse(deploy.spec.template.metadata.annotations['kubectl.kubernetes.io/restartedAt'])
                except:
                    restartedAt = currentTime - timedelta(days=1)

                if ((currentTime - restartedAt).total_seconds() / 60.0) > 1:
                    self.logs.info({'message': 'Deployment set to restart.', 'namespace': namespace, 'deployment': deployName, 'restartTime': str(restartTime), 'currentTime': str(currentTime)})
                    self.k8s.rolloutDeployment(namespace, deployName)

    def execute(self):
        # Current time in UTC format
        currentTime = datetime.now(tz=timezone.utc)

        # For each namespace
        self.logs.info({'message': 'Getting list of namespaces.'})
        namespaces = self.k8s.getNamespaces()
        for namespace in namespaces:
            namespaceName = namespace.metadata.name

            # For each deployment inside the namespace
            deployments = self.k8s.getDeployments(namespaceName)
            for deploy in deployments:
                deployName = deploy.metadata.name
                try:
                    self.__start__(namespaceName, deploy, currentTime)
                    self.__stop__(namespaceName, deploy, currentTime)
                    self.__restart__(namespaceName, deploy, currentTime)
                except:
                    self.logs.error(
                        {'message': 'Error in annotations', 'namespace': namespaceName, 'deployment': deployName})
