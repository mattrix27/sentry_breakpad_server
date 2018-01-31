import boto3
import os

import process_dump

class bucket_manager():
	def __init__(self, bucket_type = 's3', bucket_name = 'breakpad-vivint-com', directory = 'dump_files/unprocessed/'):
		self.client = boto3.client(bucket_type)
		self.resource = boto3.resource(bucket_type)
		self.my_bucket = self.resource.Bucket(bucket_name)
		self.directory = directory

	def get_files(self, Prefix):
		return self.my_bucket.objects.filter(Prefix = Prefix)

	def display_all(self, Prefix = 'v1/dump/'):
		files = self.get_files(Prefix)
		for file in files:
			print(file)
			path, filename = os.path.split(file.key)
			print(filename)	
		return 

	def download_all(self, Prefix = 'v1/dump/'):
		files = self.get_files(Prefix)
		for file in files:
			path, filename = os.path.split(file.key)
			self.my_bucket.download_file(file.key, self.directory + filename)

	def wipe(self, Prefix = 'v1/dump/'):
		files = self.get_files(Prefix)
		for file in files:
			file.delete()

	def walk(self, Prefix = 'v1/dump/'):
		files = self.get_files(Prefix)
		for file in files:
			path, filename = os.path.split(file.key)
			print(filename)
			self.my_bucket.download_file(file.key, self.directory + filename)
			process_dump.process_file(self.directory + filename)
			file.delete()

# hey = bucket_manager()
# hey.download_all()
