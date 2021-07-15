import datetime
import pytz
import urllib3
from kubernetes import client, config

class K8s:

	def __init__(self, apiEndpoint:str='', token:str=''):
		# Client via Bearer token
		if token:
			urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
			configuration = client.Configuration()
			configuration.api_key['authorization'] = token
			configuration.api_key_prefix['authorization'] = 'Bearer'
			configuration.verify_ssl = False
			configuration.host = apiEndpoint
			self.CoreV1Api = client.CoreV1Api(client.ApiClient(configuration))
			self.AppsV1Api = client.AppsV1Api(client.ApiClient(configuration))
			self.ExtensionsV1beta1Api = client.ExtensionsV1beta1Api(client.ApiClient(configuration))
		# Client via in-cluster configuration, running inside a pod with proper service account
		else:
			config.load_incluster_config()
			self.CoreV1Api = client.CoreV1Api()
			self.AppsV1Api = client.AppsV1Api()
			self.ExtensionsV1beta1Api = client.ExtensionsV1beta1Api()

	def getNamespaces(self) -> list:
		'''
			Returns a list of namespaces.
		'''
		response = self.CoreV1Api.list_namespace()
		return response.items

	def getDeployments(self, namespace:str, labelSelector:str=False) -> list:
		'''
			Returns all deployments from a namespace.
			Label selector should be an string "app=kube-web-view".
		'''
		if labelSelector:
			response = self.AppsV1Api.list_namespaced_deployment(namespace=namespace, label_selector=labelSelector)
		else:
			response = self.AppsV1Api.list_namespaced_deployment(namespace=namespace)
		return response.items

	def getDeployment(self, namespace:str, deploymentName:str):
		'''
			Returns a particular deployment.
		'''
		return self.AppsV1Api.read_namespaced_deployment(namespace=namespace, name=deploymentName)

	def getPods(self, namespace:str, labelSelector:str, limit:int=1) -> list:
		'''
			Returns a list of pods for the label selector.
			Label selector should be an string "app=kube-web-view".
		'''
		response = self.CoreV1Api.list_namespaced_pod(namespace=namespace, label_selector=labelSelector, limit=limit)
		return response.items

	def getPodsByDeployment(self, namespace:str, deploymentName:str, limit:int=1) -> list:
		'''
			Returns a list of pods related to a deployment.
		'''
		deploy = self.getDeployment(namespace, deploymentName)
		matchLabels = deploy.spec.selector.match_labels
		labelSelector = ''
		for key, value in matchLabels.items():
			labelSelector += key+'='+value+','
		labelSelector = labelSelector[:-1] # remove the last comma from the string
		return self.getPods(namespace, labelSelector, limit)

	def deleteAllPods(self, namespace:str, labelSelector:str):
		'''
			Delete all pods from a namespace filter by label selector.
		'''
		deployments = self.getDeployments(namespace=namespace, labelSelector=labelSelector)
		deployment = deployments[0]
		for labelKey, labelValue in deployment.spec.selector.match_labels.items():
			pods = self.getPods(namespace, labelKey+'='+labelValue)
			for pod in pods:
				self.deletePod(namespace=namespace, podName=pod.metadata.name)
		return True

	def setReplicas(self, namespace:str, deploymentName:str, replicas:int):
		'''
			Set the number of replicas of a deployment.
		'''
		currentScale = self.AppsV1Api.read_namespaced_deployment_scale(namespace=namespace, name=deploymentName)
		currentScale.spec.replicas = replicas
		self.AppsV1Api.replace_namespaced_deployment_scale(namespace=namespace, name=deploymentName, body=currentScale)

	def getReplicas(self, namespace:str, deploymentName:str):
		'''
			Returns the number of replicas of a deployment.
		'''
		return self.AppsV1Api.read_namespaced_deployment_scale(namespace=namespace, name=deploymentName)

	def rolloutDeployment(self, namespace:str, deploymentName:str):
		'''
			Execute a rollout restart deployment.
		'''
		deploymentManifest = self.getDeployment(namespace, deploymentName)
		deploymentManifest.spec.template.metadata.annotations = {"kubectl.kubernetes.io/restartedAt": datetime.datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()}
		self.AppsV1Api.replace_namespaced_deployment(namespace=namespace, name=deploymentName, body=deploymentManifest)

	def getIngress(self, namespace, ingressName):
		response = self.ExtensionsV1beta1Api.read_namespaced_ingress(namespace=namespace, name=ingressName)
		return response

	def getLogs(self, namespace, podName, containerName, tailLines):
		response = self.CoreV1Api.read_namespaced_pod_log(namespace=namespace, name=podName, container=containerName, tail_lines=tailLines)
		return response

	def getReplicaSet(self, namespace, labelSelector):
		response = self.AppsV1Api.list_namespaced_replica_set(namespace=namespace, label_selector=labelSelector)
		return response.items

	def deletePod(self, namespace, podName):
		response = self.CoreV1Api.delete_namespaced_pod(namespace=namespace, name=podName, body={})
		return response
