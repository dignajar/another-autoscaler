from datetime import datetime
from os import environ
import json

class Logs:
	def __init__(self, objectName:str):
		self.level = 'INFO'
		if "LOG_LEVEL" in environ:
			self.level = environ["LOG_LEVEL"]

		self.format = 'TEXT'
		if "LOG_FORMAT" in environ:
			self.format = environ["LOG_FORMAT"]

		self.objectName = objectName

	def __print__(self, level:str, extraFields:dict={}):
		fields = {
			'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			'level': level,
			'objectName': self.objectName
		}

		# Include extra fields custom by the user
		fields.update(extraFields)

		if self.format == 'JSON':
			print(json.dumps(fields))
		else:
			print(' - '.join(map(str, fields.values())))

	def error(self, extraFields:dict={}):
		if self.level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
			self.__print__('ERROR',extraFields)

	def warning(self, extraFields:dict={}):
		if self.level in ['DEBUG', 'INFO', 'WARNING']:
			self.__print__('WARNING',extraFields)

	def info(self, extraFields:dict={}):
		if self.level in ['DEBUG', 'INFO']:
			self.__print__('INFO',extraFields)

	def debug(self, extraFields:dict={}):
		if self.level in ['DEBUG']:
			self.__print__('DEBUG',extraFields)