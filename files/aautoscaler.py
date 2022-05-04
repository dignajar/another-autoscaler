import os
from croniter import croniter
from datetime import datetime, timezone, timedelta
from dateutil import parser
from deployments import Deployments
from cronjobs import Cronjobs
from logs import Logs
from k8s import K8s


class AAutoscaler:

    def __init__(self):
        self.logs = Logs(self.__class__.__name__)
        self.k8s = K8s.getInstance()
        self.deployments = Deployments()
        self.cronjobs = Cronjobs()

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
                self.deployments.__start__(namespaceName, deploy, currentTime)
                self.deployments.__stop__(namespaceName, deploy, currentTime)
                self.deployments.__restart__(
                    namespaceName, deploy, currentTime
                )
             # For each deployment inside the namespace
            cronjobs = self.k8s.getCronjobs(namespaceName)
            for cronjob in cronjobs:
                self.cronjobs.__enable__(namespaceName, cronjob, currentTime)
                self.cronjobs.__suspend__(namespaceName, cronjob, currentTime)
