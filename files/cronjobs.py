from datetime import datetime, timezone, timedelta
from croniter import croniter
from dateutil import parser
from k8s import K8s
from logs import Logs


class Cronjobs:

    def __init__(self):
        self.logs = Logs(self.__class__.__name__)
        self.k8s = K8s.getInstance()

    def __enable__(self, namespace: str, cronjob: dict, currentTime: datetime):
        '''
            Logic for enable a cronjob
        '''
        cronjobName = cronjob.metadata.name
        cronjobAnnotations = cronjob.metadata.annotations
        cronjobSuspend = cronjob.spec.suspend

        startAnnotation = 'another-autoscaler/start-time'
        if startAnnotation not in cronjobAnnotations:
            return

        self.logs.debug({'message': 'Start time detected.',
                        'namespace': namespace, 'cronjob': cronjobName})
        startTime = cronjobAnnotations[startAnnotation]

        try:
            if not croniter.match(startTime, currentTime):
                return
        except:
            self.logs.error(
                {'message': 'Error in start-time annotation', 'namespace': namespace, 'cronjob': cronjobName})
            return

        self.logs.debug({'message': 'Start time Cron expression matched.', 'namespace': namespace,
                        'cronjob': cronjobName, 'startTime': str(startTime), 'currentTime': str(currentTime)})

        if not cronjobSuspend:
            return

        self.logs.info({'message': 'Cronjob set to enabled.', 'namespace': namespace, 'cronjob': cronjobName,
                        'startTime': str(startTime)})
        self.k8s.setEnabled(namespace, cronjobName)

    def __suspend__(self, namespace: str, cronjob: dict, currentTime: datetime):
        '''
            Logic for suspend a cronjob
        '''
        cronjobName = cronjob.metadata.name
        cronjobAnnotations = cronjob.metadata.annotations
        cronjobSuspend = cronjob.spec.suspend

        stopAnnotation = 'another-autoscaler/stop-time'
        if stopAnnotation not in cronjobAnnotations:
            return

        self.logs.debug({'message': 'Stop time detected.',
                        'namespace': namespace, 'cronjob': cronjobName})
        stopTime = cronjobAnnotations[stopAnnotation]

        try:
            if not croniter.match(stopTime, currentTime):
                return
        except:
            self.logs.error(
                {'message': 'Error in stop-time annotation', 'namespace': namespace, 'cronjob': cronjobName})
            return

        self.logs.debug({'message': 'Stop time Cron expression matched.', 'namespace': namespace,
                        'cronjob': cronjobName, 'stopTime': str(stopTime), 'currentTime': str(currentTime)})

        if cronjobSuspend:
            return

        self.logs.info({'message': 'Cronjob set to suspend.', 'namespace': namespace, 'cronjob': cronjobName,
                        'stopTime': str(stopTime)})
        self.k8s.setSuspended(namespace, cronjobName)
