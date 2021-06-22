import os
from croniter import croniter
from datetime import datetime,timezone,timedelta
from dateutil import parser
from logs import Logs
from k8s import K8s

class Logic:

	def __init__(self):
		self.logs = Logs(self.__class__.__name__)

		# K8s client object
		# Auth via Bearer token
		if 'BEARER_TOKEN' in os.environ:
			self.logs.debug({'message': 'Kubernetes object via bearer token.'})
			import urllib3
			urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
			k8sAPI = os.environ.get('K8S_API_ENDPOINT')
			k8sToken = os.environ.get('BEARER_TOKEN')
			self.k8s = K8s(k8sAPI, k8sToken)
		# Auth via in-cluster configuration, running inside a pod
		elif 'KUBERNETES_SERVICE_HOST' in os.environ:
			self.logs.debug({'message': 'Kubernetes object via in-cluster configuration.'})
			self.k8s = K8s()
		else:
			raise Exception('Error trying to create the Kubernetes object.')

	def test(self):
		for namespace in self.k8s.getNamespaces():
			print(namespace.metadata.name)

	def execute(self):
		currentTime = datetime.now(tz=timezone.utc)

		# For each namespace
		namespaces = self.k8s.getNamespaces()
		for namespace in namespaces:

			# For each deployment inside the namespace
			namespaceName = namespace.metadata.name
			deployments = self.k8s.getDeployments(namespaceName)
			for deploy in deployments:
				deployName = deploy.metadata.name
				deployAnnotations = deploy.metadata.annotations

				# start-time
				startAnnotation = 'another-scheduler.io/start-time'
				if startAnnotation in deployAnnotations:
					self.logs.debug({'message': 'Start time detected.', 'namespace': namespaceName, 'deployment': deployName})
					startTime = deployAnnotations[startAnnotation]

					if croniter.match(startTime, currentTime):
						self.logs.debug({'message': 'Start time Cron expression matched.', 'namespace': namespaceName, 'deployment': deployName, 'startTime': str(startTime), 'currentTime': str(currentTime)})

						# start-replicas
						startReplicas = 1
						startReplicasAnnotation = 'another-scheduler.io/start-replicas'
						if startReplicasAnnotation in deployAnnotations:
							self.logs.debug({'message': 'Start replicas defined by the user.', 'namespace': namespaceName, 'deployment': deployName, 'replicas': deployAnnotations[startReplicasAnnotation]})
							startReplicas = int(deployAnnotations[startReplicasAnnotation])

						if deploy.spec.replicas != startReplicas:
							self.logs.info({'message': 'Deployment set to start.', 'namespace': namespaceName, 'deployment': deployName, 'startTime': str(startTime), 'availableReplicas': deploy.status.available_replicas})
							try:
								self.k8s.setReplicas(namespaceName, deployName, startReplicas)
							except:
								self.logs.error({'message': 'There was an error increasing the replicas, don\'t worry, we\'ll try again.'})

				# Stop
				stopAnnotation = 'another-scheduler.io/stop-time'
				if stopAnnotation in deployAnnotations:
					self.logs.debug({'message': 'Stop time detected.', 'namespace': namespaceName, 'deployment': deployName})
					stopTime = deployAnnotations[stopAnnotation]

					if croniter.match(stopTime, currentTime):
						self.logs.debug({'message': 'Stop time Cron expression matched.', 'namespace': namespaceName, 'deployment': deployName, 'stopTime': str(stopTime), 'currentTime': str(currentTime)})

						# stop-replicas
						stopReplicas = 0
						stopReplicasAnnotation = 'another-scheduler.io/stop-replicas'
						if stopReplicasAnnotation in deployAnnotations:
							self.logs.debug({'message': 'Stop replicas defined by the user.', 'namespace': namespaceName, 'deployment': deployName, 'replicas': deployAnnotations[stopReplicasAnnotation]})
							stopReplicas = int(deployAnnotations[stopReplicasAnnotation])

						if deploy.spec.replicas != stopReplicas:
							self.logs.info({'message': 'Deployment set to stop.', 'namespace': namespaceName, 'deployment': deployName, 'stopTime': str(stopTime), 'availableReplicas': deploy.status.available_replicas})
							try:
								self.k8s.setReplicas(namespaceName, deployName, stopReplicas)
							except:
								self.logs.error({'message': 'There was an error decreasing the replicas, don\'t worry, we\'ll try again.'})

				# Restart
				restartAnnotation = 'another-scheduler.io/restart-time'
				if restartAnnotation in deployAnnotations:
					self.logs.debug({'message': 'Restart time detected.', 'namespace': namespaceName, 'deployment': deployName})
					restartTime = deployAnnotations[restartAnnotation]

					if croniter.match(restartTime, currentTime):
						self.logs.debug({'message': 'Restart time Cron expression matched.', 'namespace': namespaceName, 'deployment': deployName, 'restartTime': str(restartTime), 'currentTime': str(currentTime)})

						try:
							restartedAt = parser.parse(deploy.spec.template.metadata.annotations['kubectl.kubernetes.io/restartedAt'])
						except:
							restartedAt = currentTime - timedelta(days=1)

						if ((currentTime - restartedAt).total_seconds() / 60.0) > 1:
							self.logs.info({'message': 'Deployment set to restart.', 'namespace': namespaceName, 'deployment': deployName, 'restartTime': str(restartTime), 'currentTime': str(currentTime)})
							self.k8s.rolloutDeployment(namespaceName, deployName)
