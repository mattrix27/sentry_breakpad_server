'''Hi, so this is the first helper script in our breakpad server. So it is initiated called from antenna in 'breakpad_resource.py' after a crash dump is saved to the bucket (which we have defaulted for our purposes, but you can change when initiating or something. Most of these functions aren't used in our production but they're fairly straightforward '''
import boto3
import os

import process_dump

class bucket_manager():

        #creates that young client to the S3 bucket in order to access, as well the directory to use, hella nice
        def __init__(self, bucket_type = 's3', bucket_name = 'breakpad-vivint-com', directory = 'dump_files/unprocessed/'):
                self.client = boto3.client(bucket_type)
                self.resource = boto3.resource(bucket_type)
                self.my_bucket = self.resource.Bucket(bucket_name)
                self.directory = directory

        #gets the files in the given path
        def get_files(self, Prefix):
                return self.my_bucket.objects.filter(Prefix = Prefix)

        #...displays the files in the path
        def display_all(self, Prefix = 'v1/dump/'):
                files = self.get_files(Prefix)
                for file in files:
                        print(file)
                        path, filename = os.path.split(file.key)
                        print(filename)
                return

        #...you got it
        def download_all(self, Prefix = 'v1/dump/'):
                files = self.get_files(Prefix)
                for file in files:
                        path, filename = os.path.split(file.key)
                        self.my_bucket.download_file(file.key, self.directory + filename)

        #deletes every in the buckets path, turns out deleting from a bucket is $$$$ tho
        def wipe(self, Prefix = 'v1/dump/'):
                files = self.get_files(Prefix)
                for file in files:
                        file.delete()

        #Alright, so this is the main function that is used, basically it gets the file(s) from the given prefix, downloads it to the set up directory, then call the function from the process_dump script to then do more stuff
        def walk(self, Prefix = 'v1/dump/'):
                files = self.get_files(Prefix)
                for file in files:
                        path, filename = os.path.split(file.key)
                        print('\n')
                        print(filename)
                        print('FILE.KEY', file.key)
                        print('\n')
                        os.chdir('/home/matthew.tung/sentry_breakpad_server')
                        self.my_bucket.download_file(file.key, self.directory + filename)
                        process_dump.process_file(self.directory + filename)
                        #file.delete()





